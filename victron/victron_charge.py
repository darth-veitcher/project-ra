"""
--- Victron ArbitCharge ---

Script to automate, via ModbusTCP, the charging of batteries using
an off-peak utility tariff.

Author: James Veitch
Date: September 2022
"""
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from os import environ, makedirs
from pathlib import Path
from time import sleep
from typing import List, Tuple  # needed for < 3.9 compat

from pymodbus.client import ModbusTcpClient

# --- LOGGING
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=format)
log = logging.getLogger(__name__ if __name__ != "__main__" else "charger")
LOG_LEVEL: str = environ.get("LOG_LEVEL", "INFO")
log.setLevel(logging._nameToLevel[LOG_LEVEL])
log.info(f"Logging started and set to ({log.level}: {logging._levelToName[log.level]})")
LOG_FILE: str = environ.get("LOG_FILE", "~/.logs/charger.log")
try:
    LOG_FILE = Path(LOG_FILE).expanduser()
except Exception as e:
    log.error(e)
    log.critical(f"Unable to use log file of {LOG_FILE}. Terminating.")
    sys.exit(1)
makedirs(LOG_FILE.parent, exist_ok=True)
fh: RotatingFileHandler = RotatingFileHandler(
    LOG_FILE, mode="a+", maxBytes=2048, backupCount=3, encoding="utf-8"
)
fh.setFormatter(logging.Formatter(format))
log.addHandler(fh)
log.info(f"Log file can be found at {fh.baseFilename}")

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
    environ.get("CHARGER_START_TIME", "00:30"), "%H:%M"
).time()
CHARGER_FINISH_TIME: datetime = datetime.strptime(
    environ.get("CHARGER_FINISH_TIME", "04:30"), "%H:%M"
).time()

# charger state management
@dataclass
class ChargerState:
    code: int
    name: str


CHARGER_POTENTIAL_STATES: List[ChargerState] = [
    ChargerState(0, "Off"),
    ChargerState(1, "On"),
    ChargerState(2, "Error"),
    ChargerState(3, "Unavailable - Unknown"),
]

RETRIES: int = 0


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
    max_retries: int = 5,
):
    global RETRIES
    current_state: ChargerState = get_charger_state()
    desired_state: ChargerState = _find_state_by_code(state_code)
    if current_state != desired_state:
        log.info(f"Changing charger state from {current_state} --> {desired_state}")
        with get_client() as client:
            _ = client.write_registers(address, desired_state.code, slave=unit_id)
        sleep(3)
        current_state: ChargerState = get_charger_state()
        if current_state != desired_state:
            RETRIES += 1
            if RETRIES > max_retries:
                log.critical("Unable to change state. Max retries exceeded.")
                return
            log.error(
                f"Unable to confirm state change. Retrying (attempt: {RETRIES}) ..."
            )
            set_charger_state(unit_id, address, state_code)
    else:
        log.info(f"Charger state is already {current_state}")


def _get_start_and_finish_datetimes(
    start: datetime = CHARGER_START_TIME, finish: datetime = CHARGER_FINISH_TIME
) -> Tuple[datetime, datetime]:
    now: datetime = datetime.now()
    start: datetime = datetime(
        now.year, now.month, now.day, CHARGER_START_TIME.hour, CHARGER_START_TIME.minute
    )
    finish: datetime = datetime(
        now.year,
        now.month,
        now.day,
        CHARGER_FINISH_TIME.hour,
        CHARGER_FINISH_TIME.minute,
    )
    if start < finish:
        return start, finish
    else:
        return start, (finish + timedelta(days=1))


def main():
    timenow = datetime.now()
    start, finish = _get_start_and_finish_datetimes()
    log.info(f"Running between {start} and {finish}")

    while start <= timenow < finish:
        timenow = datetime.now()

        # Get battery SoC and determine whether charging required still
        battery_soc: int = get_battery_soc()
        battery_needs_charging: bool = BATTERY_MIN_SOC <= battery_soc < BATTERY_MAX_SOC

        if battery_needs_charging:
            set_charger_state(state_code=1)
        else:
            log.info(
                f"Battery no longer needs charging at {battery_soc}%. Disabling charger."
            )
            set_charger_state(state_code=0)

        sleep(60)

    log.info(f"Time of {timenow} is outside of charge window. Disabling charger.")
    set_charger_state(state_code=0)


if __name__ == "__main__":
    main()
