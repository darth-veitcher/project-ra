---
title: Home Assistant Integration
---

!!! example

    This is an optional step to help to integrate the exposed ModbusTCP services from the Victron devices with a Home Assistant instance.

In order to integrate our above ModbusTCP understanding into Home Assistant we need to perform a few steps:

1. Enable the `Modbus` extension - inside the `configuration.yaml`;
2. Provide this extension with a list of available services and how to interpret them - inside the `modbus.yaml`; and
3. Explain how to translate the returned enums into human readable responses - inside the `sensor/modbus_sensor.yaml` file.

### Modbus extension: `configuration.yaml`

Home Assistant comes with an inbuilt extension to support the Modbus protocol. Full documentation can be found [here](https://www.home-assistant.io/integrations/modbus). The extension needs to be enabled within the `configuration.yaml` file however as opposed to being added via the UI.

```yaml title="configuration.yaml"
--8<-- "home-assistant/configuration.yaml:21:24"
```

We're going to follow a separation of concerns and keep our modbus service configuration in a separate file called `modbus.yaml`. Our templates (for displaying enums) will be within a dedicated `sensor/sensor_modbus.yaml` file. The folder structure will therefore look as follows:

```zsh
config
├── configuration.yaml
├── modbus.yaml
├── secrets.yaml
└── sensor
    └── sensor_modbus.yaml
```

### Services: `modbus.yaml`

The `modbus.yaml` file configures the extension with the known endpoints for our Cerbo GX, the connected devices, and their capabilities (published as services). An example is given below, simply add additional entries into the `sensors` section the mapping of yaml to the spreadsheet above should be fairly obvious, with the exception of the `scale` (needs to be `1 / [scalefactor]`) and `precision` (how accurate the value is in decimal places).

```yaml title="modbus.yaml"
--8<-- "home-assistant/modbus.yaml:9:245"
```

### Templates: `sensor/sensor_modbus.yaml`

This has to be done in hideous yaml unfortunately using jinja2 syntax... We use `if` `then` `else` type flows in order to return the correct human readable representation of the enum.

**NB:** Note how we are referencing `battery_state_system` as the root sensor. Home Assistant will automatically escape the human readable "Battery state (System)" description given to it in our `modbus.yaml` file originally.

```yaml title="sensor/sensor_modbus.yaml"
--8<-- "home-assistant/sensor/sensor_modbus.yaml"
```

You should now be able to create a card within Home Assistant that contains the details and history for the system battery.

![basic ui card](../assets/example-lovelace-card-read-battery.png)

## Sources

Thanks to the following for resources used in this process of learning:

- [Victron Energy Forums: HA Modbus Integration Tutorial](https://community.victronenergy.com/questions/78971/home-assistant-modbus-integration-tutorial.html)
- [lucode/home-assistant](https://github.com/lucode/home-assistant)
- [Home Assistant: Modbus](https://www.home-assistant.io/integrations/modbus)
- [Victron Energy: GC Modbus-TCP Manual](https://www.victronenergy.com/live/ccgx:modbustcp_faq)
