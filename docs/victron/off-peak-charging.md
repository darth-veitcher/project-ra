---
title: Off-peak Charging from Grid
---

Using the previously exposed [modbus](victron.md) services I'm using a basic python script in order to toggle my battery charger on/off. This allows me to top up my batteries overnight to 100% using grid power using my energy provider's cheap tariff (circa. 25% of normal cost, designed for EVs).

```py title="charge.py"
--8<-- "victron/victron_charge.py"
```
