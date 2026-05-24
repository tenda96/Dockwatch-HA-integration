"""Sensor platform for Dockwatch."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN
from .coordinator import DockwatchDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Dockwatch sensors from a config entry."""
    coordinator: DockwatchDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    known_containers: set[str] = set()

    summary_entities: list[SensorEntity] = [
        DockwatchTotalContainersSensor(coordinator, entry),
        DockwatchRunningContainersSensor(coordinator, entry),
        DockwatchDownContainersSensor(coordinator, entry),
    ]
    async_add_entities(summary_entities)

    def add_missing_container_entities() -> None:
        """Add sensors for containers that are not represented yet."""
        new_entities: list[SensorEntity] = []

        for container_name in sorted(coordinator.containers_by_name):
            if container_name in known_containers:
                continue

            known_containers.add(container_name)
            new_entities.append(
                DockwatchContainerStatusSensor(coordinator, entry, container_name)
            )

        if new_entities:
            async_add_entities(new_entities)

    add_missing_container_entities()
    entry.async_on_unload(coordinator.async_add_listener(add_missing_container_entities))


class DockwatchBaseSensor(CoordinatorEntity[DockwatchDataUpdateCoordinator], SensorEntity):
    """Base Dockwatch sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DockwatchDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the base sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Dockwatch",
            model="Docker monitor",
        )


class DockwatchTotalContainersSensor(DockwatchBaseSensor):
    """Sensor for total containers."""

    _attr_name = "Total containers"
    _attr_icon = "mdi:docker"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: DockwatchDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_total_containers"

    @property
    def native_value(self) -> int:
        """Return the total container count."""
        return len(self.coordinator.containers)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return useful summary attributes."""
        return {
            "containers": sorted(self.coordinator.containers_by_name),
        }


class DockwatchRunningContainersSensor(DockwatchBaseSensor):
    """Sensor for running containers."""

    _attr_name = "Running containers"
    _attr_icon = "mdi:check-circle"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: DockwatchDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_running_containers"

    @property
    def native_value(self) -> int:
        """Return the running container count."""
        return len(_containers_with_status(self.coordinator.containers, running=True))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return running container names."""
        return {
            "running_containers": _containers_with_status(
                self.coordinator.containers,
                running=True,
            ),
        }


class DockwatchDownContainersSensor(DockwatchBaseSensor):
    """Sensor for non-running containers."""

    _attr_name = "Down containers"
    _attr_icon = "mdi:alert-circle"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: DockwatchDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_down_containers"

    @property
    def native_value(self) -> int:
        """Return the non-running container count."""
        return len(_containers_with_status(self.coordinator.containers, running=False))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return non-running container names."""
        return {
            "down_containers": _containers_with_status(
                self.coordinator.containers,
                running=False,
            ),
        }


class DockwatchContainerStatusSensor(DockwatchBaseSensor):
    """Sensor representing a single Docker container status."""

    _attr_icon = "mdi:docker"

    def __init__(
        self,
        coordinator: DockwatchDataUpdateCoordinator,
        entry: ConfigEntry,
        container_name: str,
    ) -> None:
        """Initialize the container sensor."""
        super().__init__(coordinator, entry)
        self._container_name = container_name
        self._attr_name = container_name
        self._attr_unique_id = (
            f"{entry.entry_id}_container_{slugify(container_name)}"
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self._container_name in self.coordinator.containers_by_name
        )

    @property
    def native_value(self) -> str:
        """Return the container status."""
        container = self.coordinator.containers_by_name.get(self._container_name)
        if not container:
            return STATE_UNKNOWN

        return str(container.get("status") or STATE_UNKNOWN)

    @property
    def icon(self) -> str:
        """Return a status-aware icon."""
        status = self.native_value.lower()
        if status == "running":
            return "mdi:docker"
        if status in {"exited", "stopped", "dead"}:
            return "mdi:docker-off"
        return "mdi:docker"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return Dockwatch container attributes."""
        container = self.coordinator.containers_by_name.get(self._container_name)
        if not container:
            return {"missing": True}

        return dict(container)


def _containers_with_status(
    containers: list[dict[str, Any]],
    *,
    running: bool,
) -> list[str]:
    """Return container names filtered by running/non-running status."""
    names: list[str] = []

    for container in containers:
        name = container.get("name")
        status = str(container.get("status", "")).lower()
        is_running = status == "running"

        if name and is_running is running:
            names.append(str(name))

    return sorted(names)
