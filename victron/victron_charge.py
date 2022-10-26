"""
--- Victron ArbitCharge ---

Script to automate, via ModbusTCP, the charging of batteries using
an off-peak utility tariff.

Author: James Veitch
Date: September 2022
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from os import environ
from time import sleep

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# --- LOGGING
format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=format)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# --- VARIABLES
# read from environment or commandline
VENUS_IP_OR_HOSTNAME: str = environ.get("VENUS_IP_OR_HOSTNAME", "einstein.local")
BATTERY_SLAVE_UNIT_ID: int = environ.get("BATTERY_SLAVE_UNIT_ID", 100)
BATTERY_STATE_REGISTER_ADDRESS: int = environ.get("BATTERY_STATE_REGISTER_ADDRESS", 843)
BATTERY_SCALE_FACTOR: float = environ.get("BATTERY_SCALE_FACTOR", 1)
BATTERY_MIN_SOC: int = environ.get("BATTERY_MIN_SOC", 50)
BATTERY_MAX_SOC: int = environ.get("BATTERY_MAX_SOC", 100)

CHARGER_SLAVE_UNIT_ID: int = environ.get("CHARGER_SLAVE_UNIT_ID", 100)
CHARGER_STATE_REGISTER_ADDRESS: int = environ.get(
    "CHARGER_STATE_REGISTER_ADDRESS", 2317
)
CHARGER_START_TIME: datetime = datetime.strptime(
    environ.get("CHARGER_START_TIME", None), "%H:%M"
).time()
CHARGER_FINISH_TIME: datetime = datetime.strptime(
    environ.get("CHARGER_FINISH_TIME", None), "%H:%M"
).time()

# charger state management
@dataclass
class ChargerState:
    code: int
    name: str


CHARGER_POTENTIAL_STATES: list[ChargerState] = [
    ChargerState(0, "Off"),
    ChargerState(1, "On"),
    ChargerState(2, "Error"),
    ChargerState(3, "Unavailable - Unknown"),
]


# --- MAIN CODE
def _find_state_by_code(code: int) -> ChargerState:
    state = [state for state in CHARGER_POTENTIAL_STATES if state.code == code]
    return state[0] if len(state) == 1 else None


def get_client(host: str = VENUS_IP_OR_HOSTNAME) -> ModbusTcpClient:
    return ModbusTcpClient(host)


def get_battery_soc(
    unit_id: int = BATTERY_SLAVE_UNIT_ID,
    address: int = BATTERY_STATE_REGISTER_ADDRESS,
    scale_factor: float = BATTERY_SCALE_FACTOR,
):
    with get_client() as client:
        response = client.read_holding_registers(address, slave=unit_id)
        charge: int = response.registers[0]
        return round(float(charge) / scale_factor)


def get_charger_state(
    unit_id: int = CHARGER_SLAVE_UNIT_ID, address: int = CHARGER_STATE_REGISTER_ADDRESS
) -> ChargerState:
    with get_client() as client:
        response = client.read_holding_registers(address, slave=unit_id)
        state_code: int = response.registers[0]
        state: ChargerState = _find_state_by_code(state_code)
        return state


def set_charger_state(
    unit_id: int = CHARGER_SLAVE_UNIT_ID,
    address: int = CHARGER_STATE_REGISTER_ADDRESS,
    state_code: int = 1,
):
    current_state: ChargerState = get_charger_state()
    desired_state: ChargerState = _find_state_by_code(state_code)
    if current_state != desired_state:
        log.info(f"Changing charger state from {current_state} --> {desired_state}")
        with get_client() as client:
            response = client.write_registers(
                address, desired_state.code, slave=unit_id
            )
            log.debug(vars(response))
        current_state: ChargerState = get_charger_state()
        if current_state != desired_state:
            log.error("Unable to confirm state change. Retrying ...")
            set_charger_state(unit_id, address, state_code)
    else:
        log.info(f"Charger state is already {current_state}")


def main():
    timenow = datetime.now().time()

    while CHARGER_START_TIME <= timenow < CHARGER_FINISH_TIME:
        timenow = datetime.now().time()

        # Get battery SoC and determine whether charging required still
        battery_soc: int = get_battery_soc()
        battery_needs_charging: bool = BATTERY_MIN_SOC <= battery_soc < BATTERY_MAX_SOC

        if battery_needs_charging:
            set_charger_state(state_code=1)
        else:
            set_charger_state(state_code=0)

        sleep(60)

    log.info(f"Time of {timenow} is outside of charge window. Disabling charger.")
    set_charger_state(state_code=0)


if __name__ == "__main__":
    main()
