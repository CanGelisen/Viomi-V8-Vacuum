"""Constants for the Viomi V8 Vacuum integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "viomi_v8"

CONF_FIRMWARE = "firmware"
CONF_MAC = "mac"
CONF_MODEL = "model"

SUPPORTED_MODELS = frozenset({"viomi.vacuum.v8"})

SCAN_INTERVAL = timedelta(seconds=15)
REQUEST_TIMEOUT = 5  # seconds, per miIO request

PLATFORMS: list[Platform] = [Platform.VACUUM, Platform.SENSOR, Platform.SELECT]

SERVICE_CLEAN_ROOMS = "clean_rooms"
ATTR_ROOMS = "rooms"
ATTR_EDGE = "edge"
