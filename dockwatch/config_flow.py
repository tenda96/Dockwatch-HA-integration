import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT
from .const import DOMAIN, DEFAULT_PORT, CONF_URL

_LOGGER = logging.getLogger(__name__)

class DockwatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dockwatch."""

    async def async_step_user(self, user_input=None):
        """Handle the initial configuration step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST): str,
                        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                        vol.Required(CONF_API_KEY): str,
                    }
                ),
            )
        
        # Automatically format the host and port into a clean URL
        host = user_input[CONF_HOST]
        port = user_input[CONF_PORT]
        user_input[CONF_URL] = f"http://{host}:{port}"
        
        return self.async_create_entry(title=f"Dockwatch ({host})", data=user_input)
