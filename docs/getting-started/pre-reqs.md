---
hide:
  #   - footer
  #   - navigation
  - toc
---

!!! warning "Acceptance of Liability"

    I shouldn't really need to say this... but I will anyway. This documentation is intended for my own reference and learning. Nothing within it should be taken as official electrical guidance etc. etc. and by following any of my instructions (and tailoring for your own circumstances) you are assuming all liability for your own actions! 🤦‍♂️

Before embarking on this quest you'll need to ensure you meet some of the below pre-requisites. Whether you want to use [Home Assistant](https://www.home-assistant.io) or not is a matter of personal choice - it's not required for this. I'm including integration instructions for completeness purposes as I'll document the HA setup separately to keep this repository focussed. The custom automation I have for controlling charge of the batteries during off-peak hours is pure Python in this repository and can be run independently of any host automation controller.

## Home Assistant

There are instructions in the [getting started](https://www.home-assistant.io/getting-started/) section of the Home Assistant website. Choose your own adventure but my own personal setup uses a Docker container as part of a wider orchestration. As a result instructions will be specific to that and may need tweaking for your own environment.

## Victron Energy Devices

Regardless of if you're attending to integrate Victron Energy Devices to your Home Assistant installation or simply control them via the exposed Modbus services over TCP you'll need access to either a [Cerbo GX](https://www.victronenergy.com/panel-systems-remote-monitoring/cerbo-gx) or homebrewed [Venus OS](https://github.com/victronenergy/venus/wiki) device. For the sake of ease I've used a Cerbo GX.

This device acts as an aggregator for the Victron kit across a variety of protocols (CAN, Modbus, VE.Direct etc.) and will provide us with a single endpoint for managing them over TCP after you connect via either WiFi or Ethernet (ideally, see [lessons learned](../lessons-learned.md#youll-probably-want-the-cerbo-gx-on-ethernet)).
