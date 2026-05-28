"""Config flow for Dockwatch."""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlparse

from aiohttp import ClientError, ClientResponseError, ClientTimeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_CONTAINERS_PATH,
    CONF_SSL,
    CONF_URL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SSL,
    DOMAIN,
)


class DockwatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dockwatch."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Create the options flow."""
        return DockwatchOptionsFlowHandler()

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data = _normalize_user_input(user_input)
            await self.async_set_unique_id(f"{data[CONF_HOST]}:{data[CONF_PORT]}")
            self._abort_if_unique_id_configured(updates=data)

            try:
                await _validate_connection(self.hass, data)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                title = data.pop(CONF_NAME, DEFAULT_NAME)
                return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input),
            errors=errors,
        )


class DockwatchOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Dockwatch options."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage integration options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data = _normalize_user_input(user_input)
            title = data.pop(CONF_NAME, self.config_entry.title)

            # Save settings even if Dockwatch is currently offline.
            # This allows fixing a wrong IP/host/API key from the UI.
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                title=title,
                data={**self.config_entry.data, **data},
            )

            return self.async_create_entry(title="", data={})

        current = {
            CONF_NAME: self.config_entry.title,
            CONF_HOST: self.config_entry.data.get(CONF_HOST, ""),
            CONF_PORT: self.config_entry.data.get(CONF_PORT, DEFAULT_PORT),
            CONF_SSL: self.config_entry.data.get(CONF_SSL, DEFAULT_SSL),
            CONF_API_KEY: self.config_entry.data.get(CONF_API_KEY, ""),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(current),
            errors=errors,
        )


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Return the config/options form schema."""
    defaults = defaults or {}

    return vol.Schema(
        {
            vol.Optional(
                CONF_NAME,
                default=defaults.get(CONF_NAME, DEFAULT_NAME),
            ): str,
            vol.Required(
                CONF_HOST,
                default=defaults.get(CONF_HOST, ""),
            ): str,
            vol.Required(
                CONF_PORT,
                default=defaults.get(CONF_PORT, DEFAULT_PORT),
            ): int,
            vol.Required(
                CONF_SSL,
                default=defaults.get(CONF_SSL, DEFAULT_SSL),
            ): bool,
            vol.Required(
                CONF_API_KEY,
                default=defaults.get(CONF_API_KEY, ""),
            ): str,
        }
    )


def _normalize_user_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Normalize user input and build the Dockwatch base URL."""
    data = dict(user_input)

    host_input = str(data[CONF_HOST]).strip().rstrip("/")
    port = int(data.get(CONF_PORT, DEFAULT_PORT))
    use_ssl = bool(data.get(CONF_SSL, DEFAULT_SSL))

    if host_input.startswith(("http://", "https://")):
        parsed = urlparse(host_input)
        host = parsed.hostname or parsed.netloc
        port = parsed.port or port
        use_ssl = parsed.scheme == "https"
    else:
        host = host_input

    scheme = "https" if use_ssl else "http"

    data[CONF_HOST] = host
    data[CONF_PORT] = port
    data[CONF_SSL] = use_ssl
    data[CONF_URL] = f"{scheme}://{host}:{port}"

    return data


async def _validate_connection(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate Dockwatch connection details."""
    session = async_get_clientsession(hass)
    url = f"{data[CONF_URL].rstrip('/')}{API_CONTAINERS_PATH}"
    headers = {"X-Api-Key": data[CONF_API_KEY]}

    try:
        async with session.get(
            url,
            headers=headers,
            timeout=ClientTimeout(total=10),
        ) as response:
            if response.status in (401, 403):
                raise InvalidAuth

            response.raise_for_status()
            payload = await response.json(content_type=None)

    except asyncio.TimeoutError as err:
        raise CannotConnect from err
    except ClientResponseError as err:
        if err.status in (401, 403):
            raise InvalidAuth from err
        raise CannotConnect from err
    except ClientError as err:
        raise CannotConnect from err
    except ValueError as err:
        raise CannotConnect from err

    if not isinstance(payload, dict) or not isinstance(payload.get("response"), list):
        raise CannotConnect


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate invalid authentication."""
