import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from .sensor import CONF_DOCKER_CHECK_URL

_LOGGER = logging.getLogger(__name__)

class DockerConfigFlow(config_entries.ConfigFlow, domain="dockercheck"):
    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DOCKER_CHECK_URL): str,  
                        vol.Required(CONF_API_KEY): str,
                    }
                ),
            )
        return self.async_create_entry(title="Docker Check", data=user_input)
