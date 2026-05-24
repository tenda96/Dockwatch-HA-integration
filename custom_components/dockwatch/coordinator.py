"""Data coordinator for the Dockwatch integration."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientTimeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_CONTAINERS_PATH, CONF_URL, DOMAIN, SCAN_INTERVAL

import logging

_LOGGER = logging.getLogger(__name__)


class DockwatchDataUpdateCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Fetch Dockwatch data once and share it with all entities."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.config_entry = entry
        self._session = async_get_clientsession(hass)
        self._base_url = entry.data[CONF_URL].rstrip("/")
        self._headers = {"X-Api-Key": entry.data[CONF_API_KEY]}

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=SCAN_INTERVAL,
        )

    @property
    def containers(self) -> list[dict[str, Any]]:
        """Return the latest container list."""
        return self.data or []

    @property
    def containers_by_name(self) -> dict[str, dict[str, Any]]:
        """Return containers indexed by name."""
        return {
            str(container["name"]): container
            for container in self.containers
            if container.get("name")
        }

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch container data from Dockwatch."""
        url = f"{self._base_url}{API_CONTAINERS_PATH}"

        try:
            async with self._session.get(
                url,
                headers=self._headers,
                timeout=ClientTimeout(total=15),
            ) as response:
                if response.status in (401, 403):
                    raise UpdateFailed("Dockwatch API key non valida o non autorizzata")

                response.raise_for_status()
                payload = await response.json(content_type=None)

        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout durante la chiamata a Dockwatch") from err
        except ClientResponseError as err:
            raise UpdateFailed(f"Errore HTTP Dockwatch: {err.status}") from err
        except ClientError as err:
            raise UpdateFailed(f"Errore di connessione a Dockwatch: {err}") from err
        except ValueError as err:
            raise UpdateFailed("Risposta JSON non valida da Dockwatch") from err

        containers = payload.get("response")
        if not isinstance(containers, list):
            raise UpdateFailed("Risposta Dockwatch non valida: campo 'response' mancante")

        normalized: list[dict[str, Any]] = []
        for container in containers:
            if isinstance(container, dict):
                normalized.append(container)

        return normalized
