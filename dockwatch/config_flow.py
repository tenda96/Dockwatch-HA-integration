import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT

_LOGGER = logging.getLogger(__name__)
DOMAIN = "dockwatch"

class DockwatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dockwatch."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST): str,
                        vol.Required(CONF_PORT, default=9999): int,
                        vol.Required(CONF_API_KEY): str,
                    }
                ),
            )
        
        # Format the URL automatically
        host = user_input[CONF_HOST]
        port = user_input[CONF_PORT]
        user_input["url"] = f"http://{host}:{port}"
        
        return self.async_create_entry(title=f"Dockwatch ({host})", data=user_input)
