"""The Viomi V8 Vacuum integration (local miIO control)."""
from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .client import ViomiV8Client
from .const import PLATFORMS
from .coordinator import ViomiConfigEntry, ViomiV8Coordinator


async def async_setup_entry(hass: HomeAssistant, entry: ViomiConfigEntry) -> bool:
    try:
        client = await hass.async_add_executor_job(
            ViomiV8Client, entry.data[CONF_HOST], entry.data[CONF_TOKEN]
        )
    except Exception as err:  # noqa: BLE001
        raise ConfigEntryNotReady(f"Cannot reach vacuum: {err}") from err

    coordinator = ViomiV8Coordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ViomiConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
