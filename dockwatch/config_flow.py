import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_PORT, CONF_URL

_LOGGER = logging.getLogger(__name__)

class DockwatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dockwatch."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return DockwatchOptionsFlowHandler()

    async def async_step_user(self, user_input=None):
        """Handle the initial configuration step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Optional(CONF_NAME, default="Dockwatch"): str,
                        vol.Required(CONF_HOST): str,
                        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                        vol.Required(CONF_API_KEY): str,
                    }
                ),
            )
        
        host = user_input[CONF_HOST]
        port = user_input[CONF_PORT]
        user_input[CONF_URL] = f"http://{host}:{port}"
        
        title = user_input.pop(CONF_NAME, f"Dockwatch ({host})")
        
        return self.async_create_entry(title=title, data=user_input)


class DockwatchOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Dockwatch options (Ingranaggio)."""


    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            user_input[CONF_URL] = f"http://{host}:{port}"
            
            title = user_input.pop(CONF_NAME, self.config_entry.title)
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={**self.config_entry.data, **user_input}, title=title
            )
            
            return self.async_create_entry(title="", data={})

        current_data = self.config_entry.data
        current_name = self.config_entry.title

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=current_name): str,
                    vol.Required(CONF_HOST, default=current_data.get(CONF_HOST, "")): str,
                    vol.Required(CONF_PORT, default=current_data.get(CONF_PORT, DEFAULT_PORT)): int,
                    vol.Required(CONF_API_KEY, default=current_data.get(CONF_API_KEY, "")): str,
                }
            ),
        )
