import logging
from datetime import timedelta
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

CONF_API_KEY = "api_key"
CONF_DOCKER_CHECK_URL = "docker_check_url"  

async def async_setup_entry(hass, config_entry, async_add_entities):
    docker_host = config_entry.data[CONF_DOCKER_CHECK_URL]
    api_key = config_entry.data[CONF_API_KEY]
    scan_interval = timedelta(minutes=1)

    if not docker_host.startswith("http://") and not docker_host.startswith("https://"):
        docker_host = "http://" + docker_host

    if ":" not in docker_host.split("//")[-1]:
        _LOGGER.warning("L'host configurato (%s) non contiene la porta. Verrà usata la porta predefinita (80)", docker_host)

    _LOGGER.debug("Utilizzo host: %s", docker_host)

    session = async_get_clientsession(hass)
    headers = {"X-Api-Key": api_key}

    try:
        url = f"{docker_host}/api/stats/containers"
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            containers = data["response"]

            sensors = []
            for container in containers:
                container_name = container["name"]
                sensors.append(
                    DockerContainerSensor(
                        hass,
                        container_name,
                        docker_host, 
                        container_name,
                        scan_interval,
                        api_key,
                    )
                )
            async_add_entities(sensors)
    except Exception as e:
        _LOGGER.error("Error fetching container list: %s", e)
        return

class DockerContainerSensor(Entity):
    def __init__(self, hass, name, host, container, scan_interval, api_key):
        self.hass = hass
        self._name = name
        self._host = host  
        self._container = container
        self._state = STATE_UNKNOWN
        self.scan_interval = scan_interval
        self._attributes = {}
        self.api_key = api_key

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        session = async_get_clientsession(self.hass)
        headers = {"X-Api-Key": self.api_key}
        try:
            url = f"{self._host}/api/stats/containers"
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                containers = data["response"]

                container_data = next((c for c in containers if c["name"] == self._container), None)
                if container_data:
                    self._state = container_data.get("status", STATE_UNKNOWN)
                    self._attributes = container_data
                else:
                    self._state = STATE_UNKNOWN
                    self._attributes = {}
        except Exception as e:
            _LOGGER.error("Error fetching data from %s: %s", self._host, e)
            self._state = STATE_UNKNOWN
            self._attributes = {}
