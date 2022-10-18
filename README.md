# Project Ra

This repository is designed to document my approach to setting up a basic Home Assistant installation with a connection to Victron Energy devices (solar mppt charge controller, battery smartshunt, inverter etc.)

Many of the settings will require changing for your local configuration so please read the documentation before attempting to blindly run a `docker compose up -d`.

## Victron Energy

This section describes how to add Victron Energy devices into Home Assistant.

### Enable Modbus TCP

Go to the `remote console` for the Cerbo GX device and ensure Modbus is enabled (it's disabled by default).

Settings >> Services >> Modbus TCP >> Select `Enabled`

Next click into the `Available services` section of this menu and you should see a list of entries with familiar looking descriptions to your victron devices such as `SmartShunt` and associated `Unit ID` values (which we will require for identifying them later on).

In my setup I have the following:

| Name                             | Type         | ID  |
| -------------------------------- | ------------ | --- |
| SmartShunt 500A/50mV             | battery      | 224 |
| SmartSolar MPPT 150/100          | solarcharger | 100 |
| (no entry name)                  | system       | 100 |
| Phoenix Inverter Compact 24/1600 | vebus        | 227 |

As can be seen from the above there is a generic, unnamed `com.victron.system` type device in the list with a `Unit ID` of `100`. This is the Cerbo GX device. The `IDs` have been stored inside the `secrets.yaml` configuration file as follows:

```yaml
# file: secrets.yaml
# victron `Unit IDs` from Modbus settings
com.victronenergy.system: 100
com.victronenergy.battery: 224
com.victronenergy.vebus: 227
com.victronenergy.solarcharger: 100
```

### Modbus Device Basic Concepts

This is explained in far more detail elsewhere, including in the [Victron Energy: GC Modbus-TCP Manual](https://www.victronenergy.com/live/ccgx:modbustcp_faq), but in order to effectively utilise modbus devices we need to know both the `Unit ID` of the physical hardware and then the associated `register address` for the sensor/switch that we'd like to read/write. Whilst you can find the `Unit ID` above, the specifics for the `registers` have to be found from the manufacturers specification. In the instance of Victron they publish theirs in an Excel file that you need to download from their website. The version I am using is `CCGX-Modbus-TCP-register-list-2.90` which can be found [here](https://www.victronenergy.com/support-and-downloads/technical-information).

## Sources:

Thanks to the following for resources used in this process of learning:

- [Victron Energy Forums: HA Modbus Integration Tutorial](https://community.victronenergy.com/questions/78971/home-assistant-modbus-integration-tutorial.html)
- [lucode/home-assistant](https://github.com/lucode/home-assistant)
- [Home Assistant: Modbus](https://www.home-assistant.io/integrations/modbus)
- [Victron Energy: GC Modbus-TCP Manual](https://www.victronenergy.com/live/ccgx:modbustcp_faq)
