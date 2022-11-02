---
title: Off-peak Charging from Grid
---

Using the previously exposed [modbus](victron.md) services I'm using a basic python script in order to toggle my battery charger on/off. This allows me to top up my batteries overnight to 100% using grid power using my energy provider's cheap tariff (circa. 25% of normal cost, designed for EVs).

The only requirement you'll need can be installed with a `#!python python -m pip install 'pymodbus[serial]'`.

??? help "Automated Charging Script"

    ```py title="victron_charge.py"
    --8<-- "victron/victron_charge.py"
    ```

The above script can be hooked into something as straightforward as a cron job and checks:

- if the system time is between `CHARGER_START_TIME` and `CHARGER_FINISH_TIME`; and
- battery state of charge is between `BATTERY_MIN_SOC` and `BATTERY_MAX_SOC`.

Based on the results it will then connects to the Cerbo GX device at `VENUS_IP_OR_HOSTNAME` and set the desired charger state accordingly.
