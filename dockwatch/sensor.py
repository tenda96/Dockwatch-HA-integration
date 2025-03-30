import logging
from datetime import timedelta
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

# Costanti usate nel config flow
CONF_API_KEY = "api_key"
CONF_DOCKER_CHECK_URL = "docker_check_url"  # Si aspetta l'IP:porta, es. "192.168.1.5:9999"

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, config_entry, async_add_entities):
    docker_host = config_entry.data[CONF_DOCKER_CHECK_URL]
    api_key = config_entry.data[CONF_API_KEY]

    # Se l'host non contiene uno schema, aggiungi "http://"
    if not docker_host.startswith("http://") and not docker_host.startswith("https://"):
        docker_host = "http://" + docker_host

    # Verifica che l'host contenga la porta
    if ":" not in docker_host.split("//")[-1]:
        _LOGGER.warning("L'host configurato (%s) non contiene la porta. Verrà usata la porta predefinita (80)", docker_host)

    _LOGGER.debug("Utilizzo host: %s", docker_host)
    session = async_get_clientsession(hass)
    headers = {"X-Api-Key": api_key}

    sensors = []

    try:
        # Recupera la lista dei container dall'API
        url = f"{docker_host}/api/stats/containers"
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            containers = data.get("response", [])

            # Crea un sensore per ogni container (entità individuali)
            for container in containers:
                container_name = container.get("name", "unknown")
                sensors.append(
                    DockerContainerSensor(
                        hass,
                        container_name,
                        docker_host,
                        container_name,
                        SCAN_INTERVAL,
                        api_key,
                    )
                )
            # Aggiungi il sensore generale che aggrega tutte le info
            sensors.append(DockerOverviewSensor(hass, docker_host, api_key, SCAN_INTERVAL))
            async_add_entities(sensors, update_before_add=True)
    except Exception as e:
        _LOGGER.error("Error fetching container list: %s", e)
        return

class DockerContainerSensor(Entity):
    """Sensore individuale per ciascun container Docker."""
    def __init__(self, hass, name, host, container, scan_interval, api_key):
        self.hass = hass
        self._name = name
        self._host = host  # Host configurato (con schema e porta)
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
                containers = data.get("response", [])
                container_data = next((c for c in containers if c.get("name") == self._container), None)
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

class DockerOverviewSensor(Entity):
    """Sensore generale che aggrega le informazioni di tutti i container Docker."""
    def __init__(self, hass, host, api_key, scan_interval):
        self.hass = hass
        self._host = host
        self.api_key = api_key
        self.scan_interval = scan_interval
        self._state = STATE_UNKNOWN
        self._attributes = {}

    @property
    def name(self):
        return "Docker Containers Overview"

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
                containers = data.get("response", [])
                up_containers = []
                down_containers = []
                health_info = {}
                for container in containers:
                    name = container.get("name", "unknown")
                    status = container.get("status", "").lower()
                    health = container.get("health", "unknown")
                    if status == "running":
                        up_containers.append(name)
                        health_info[name] = health
                    else:
                        down_containers.append(name)
                        health_info[name] = health
                self._state = f"Up: {len(up_containers)}, Down: {len(down_containers)}"
                self._attributes = {
                    "up_containers": up_containers,
                    "down_containers": down_containers,
                    "health": health_info
                }
        except Exception as e:
            _LOGGER.error("Error fetching data from %s: %s", self._host, e)
            self._state = STATE_UNKNOWN
            self._attributes = {}
