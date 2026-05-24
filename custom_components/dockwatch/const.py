"""Constants for the Dockwatch integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "dockwatch"
PLATFORMS = ["sensor"]

DEFAULT_NAME = "Dockwatch"
DEFAULT_PORT = 9999
DEFAULT_SSL = False
SCAN_INTERVAL = timedelta(minutes=1)

CONF_URL = "url"
CONF_SSL = "ssl"

API_CONTAINERS_PATH = "/api/stats/containers"
