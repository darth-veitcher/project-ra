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

### Setup Configurations

We need to modfiy both the overall `configuration.yaml` as well as the `sensors.yaml` file.

```yaml
# file: configuration.yaml
# configuration entry for a TCP connection
# used for victron energy device integration
# needs to be added to the configuration.yaml
# source: https://community.victronenergy.com/questions/78971/home-assistant-modbus-integration-tutorial.html
name: victron
type: tcphost: 192.168.1.205
port: 502
```

This teall

## Sources:

Thanks to the following for resources used in this process of learning:

- [Victron Energy Forums: HA Modbus Integration Tutorial](https://community.victronenergy.com/questions/78971/home-assistant-modbus-integration-tutorial.html)
- [lucode/home-assistant](https://github.com/lucode/home-assistant)
