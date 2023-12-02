from __future__ import annotations

import asyncio
import logging
import base64
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.util.json import json_loads_object
from homeassistant.components.bluetooth import MONOTONIC_TIME, BaseHaRemoteScanner
from homeassistant.components.bluetooth import (
    async_get_advertisement_callback,
    async_register_scanner,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class JsonDatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self, scanner) -> None:
        super().__init__()
        self._scanner = scanner

    def datagram_received(self, data, addr):
        try:
            json_data = data.decode('utf-8')
            data = json_loads_object(json_data)
            self._scanner.async_on_advertisement(data)
        except ValueError as e:
            _LOGGER.debug("Error decoding JSON:", e)

def convert_base64_value_to_bytes(data: dict):
    return {key: base64.b64decode(value) for key, value in data.items()}

class JsonScanner(BaseHaRemoteScanner):

    __slots__ = ()

    @callback
    def async_on_advertisement(self, adv: dict) -> None:
        """Call the registered callback."""
        self._async_on_advertisement(
            adv["address"],
            adv["rssi"],
            adv["name"],
            adv["service_uuids"],
            convert_base64_value_to_bytes(adv["service_data"]),
            convert_base64_value_to_bytes(adv["manufacturer_data"]),
            adv["tx_power"],
            {},
            MONOTONIC_TIME(),
        )

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    new_info_callback = async_get_advertisement_callback(hass)
    connectable = False
    scanner = JsonScanner(hass, f"{DOMAIN}_scanner", entry.title, new_info_callback, None, connectable)

    unload_callbacks = [
        async_register_scanner(hass, scanner, connectable),
        scanner.async_setup(),
    ]

    transport, _ = await hass.loop.create_datagram_endpoint(
        lambda: JsonDatagramProtocol(scanner),
        local_addr=("0.0.0.0", 5038)
    )

    hass.data[DOMAIN] = [transport.close].extend(unload_callbacks)

    # setup event listeners
    async def on_hass_stop(event: Event) -> None:
        """Handle incoming stop event from Home Assistant."""
        for callback in hass.data.pop(DOMAIN, []):
            callback()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, on_hass_stop)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    for callback in hass.data.pop(DOMAIN, []):
        callback()
    return True
