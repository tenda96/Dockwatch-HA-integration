"""The Dockwatch integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Dockwatch component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Dockwatch from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Ricarica l'integrazione quando vengono salvate nuove opzioni."""
    await hass.config_entries.async_reload(entry.entry_id)
