import logging
from homeassistant.const import STATE_UNKNOWN, CONF_API_KEY
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import CONF_URL, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Dockwatch sensors from the config entry."""
    docker_host = config_entry.data[CONF_URL]
    api_key = config_entry.data[CONF_API_KEY]

    _LOGGER.debug("Starting Dockwatch integration using host: %s", docker_host)
    session = async_get_clientsession(hass)
    headers = {"X-Api-Key": api_key}

    sensors = []

    try:
        # Initial fetch to discover containers
        url = f"{docker_host}/api/stats/containers"
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            containers = data.get("response", [])

            # Add an individual sensor for each container found
            for container in containers:
                container_name = container.get("name", "unknown")
                sensors.append(
                    DockwatchContainerSensor(
                        hass,
                        container_name,
                        docker_host,
                        container_name,
                        SCAN_INTERVAL,
                        api_key,
                    )
                )

            # Add aggregation and summary sensors
            sensors.append(DockwatchOverviewSensor(hass, docker_host, api_key, SCAN_INTERVAL))
            sensors.append(DockwatchUpContainersSensor(hass, docker_host, api_key, SCAN_INTERVAL))
            sensors.append(DockwatchDownContainersSensor(hass, docker_host, api_key, SCAN_INTERVAL))

            async_add_entities(sensors, update_before_add=True)
    except Exception as e:
        _LOGGER.error("Failed to fetch container list from Dockwatch: %s", e)
        return


class DockwatchContainerSensor(Entity):
    """Sensor representing a specific Docker container."""
    def __init__(self, hass, name, host, container, scan_interval, api_key):
        self.hass = hass
        self._name = f"Dockwatch {name}"
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
        """Update container state and attributes."""
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
            _LOGGER.error("Update failed for Dockwatch container %s: %s", self._container, e)
            self._state = STATE_UNKNOWN


class DockwatchOverviewSensor(Entity):
    """Sensor for the total number of containers."""
    def __init__(self, hass, host, api_key, scan_interval):
        self.hass = hass
        self._host = host
        self.api_key = api_key
        self.scan_interval = scan_interval
        self._state = STATE_UNKNOWN
        self._attributes = {}

    @property
    def name(self):
        return "Dockwatch Containers Overview"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        """Update the total container count."""
        session = async_get_clientsession(self.hass)
        headers = {"X-Api-Key": self.api_key}
        try:
            url = f"{self._host}/api/stats/containers"
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                containers = data.get("response", [])
                total = len(containers)
                self._state = str(total)
                self._attributes = {"total_containers": total}
        except Exception as e:
            _LOGGER.error("Update failed for Dockwatch overview: %s", e)
            self._state = STATE_UNKNOWN


class DockwatchUpContainersSensor(Entity):
    """Sensor for the count of running containers."""
    def __init__(self, hass, host, api_key, scan_interval):
        self.hass = hass
        self._host = host
        self.api_key = api_key
        self.scan_interval = scan_interval
        self._state = STATE_UNKNOWN
        self._attributes = {}

    @property
    def name(self):
        return "Dockwatch Up Containers"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        """Update the count of containers with status 'running'."""
        session = async_get_clientsession(self.hass)
        headers = {"X-Api-Key": self.api_key}
        try:
            url = f"{self._host}/api/stats/containers"
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                containers = data.get("response", [])
                up_list = [c["name"] for c in containers if c.get("status", "").lower() == "running"]
                self._state = len(up_list)
                self._attributes = {"up_containers": ", ".join(up_list)}
        except Exception as e:
            _LOGGER.error("Update failed for Dockwatch running count: %s", e)
            self._state = STATE_UNKNOWN


class DockwatchDownContainersSensor(Entity):
    """Sensor for the count of non-running containers."""
    def __init__(self, hass, host, api_key, scan_interval):
        self.hass = hass
        self._host = host
        self.api_key = api_key
        self.scan_interval = scan_interval
        self._state = STATE_UNKNOWN
        self._attributes = {}

    @property
    def name(self):
        return "Dockwatch Down Containers"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        """Update the count of containers that are not running."""
        session = async_get_clientsession(self.hass)
        headers = {"X-Api-Key": self.api_key}
        try:
            url = f"{self._host}/api/stats/containers"
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                containers = data.get("response", [])
                down_list = [c["name"] for c in containers if c.get("status", "").lower() != "running"]
                self._state = len(down_list)
                self._attributes = {"down_containers": ", ".join(down_list)}
        except Exception as e:
            _LOGGER.error("Update failed for Dockwatch stopped count: %s", e)
            self._state = STATE_UNKNOWN
