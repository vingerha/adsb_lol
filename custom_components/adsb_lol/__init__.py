"""The GTFS integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from datetime import timedelta

from .const import DOMAIN, PLATFORMS, DEFAULT_PATH, DEFAULT_REFRESH_INTERVAL
from homeassistant.const import CONF_HOST
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GTFS from a config entry."""
    hass.data.setdefault(DOMAIN, {})
   
    coordinator = GTFSUpdateCoordinator(hass, entry)    

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady
      
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator
    }

    entry.async_on_unload(entry.add_update_listener(update_listener))
      
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
     
async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    hass.data[DOMAIN][entry.entry_id]['coordinator'].update_interval = timedelta(minutes=10)
    return True