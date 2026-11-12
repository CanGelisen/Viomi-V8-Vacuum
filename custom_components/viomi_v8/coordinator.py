"""Polling coordinator for the Viomi V8 vacuum."""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import ViomiV8Client
from .const import DOMAIN, SCAN_INTERVAL
from .protocol import ViomiV8Status

_LOGGER = logging.getLogger(__name__)

type ViomiConfigEntry = ConfigEntry[ViomiV8Coordinator]


class ViomiV8Coordinator(DataUpdateCoordinator[ViomiV8Status]):
    """Fetches status over local miIO and runs commands for the entities."""

    config_entry: ViomiConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: ViomiConfigEntry, client: ViomiV8Client
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {entry.title}",
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> ViomiV8Status:
        try:
            return await self.hass.async_add_executor_job(self.client.status)
        except Exception as err:  # noqa: BLE001 - miio raises many types
            raise UpdateFailed(f"Error polling vacuum: {err}") from err

    async def async_run(self, func: Callable[..., Any], *args: Any) -> Any:
        """Run a blocking client call, surface failures, then refresh state."""
        try:
            result = await self.hass.async_add_executor_job(func, *args)
        except Exception as err:  # noqa: BLE001
            raise HomeAssistantError(f"Vacuum command failed: {err}") from err
        await self.async_request_refresh()
        return result
