# Home Assistant Community Store (HACS)

To use [HACS](https://hacs.xyz) in the container we need to exec into it and run a command, then restart the service.

```zsh
# on host
docker exec -it hass bash -c 'wget -O - https://get.hacs.xyz | bash -'
```

After restarting the service you need to refresh / logout to ensure the cache is cleared for the integrations **otherwise HACS won't display.** Then go into integrations and search for HACS to install.
