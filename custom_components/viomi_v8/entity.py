"""Shared base entity."""
from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo, format_mac
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_FIRMWARE, CONF_MAC, DOMAIN
from .coordinator import ViomiV8Coordinator


class ViomiV8Entity(CoordinatorEntity[ViomiV8Coordinator]):
    """Base class: one device, one coordinator."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ViomiV8Coordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        base = entry.unique_id or entry.entry_id
        self._attr_unique_id = f"{base}_{key}"
        mac = entry.data.get(CONF_MAC)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, base)},
            connections={(CONNECTION_NETWORK_MAC, format_mac(mac))} if mac else set(),
            manufacturer="Viomi / Xiaomi",
            model="Mi Robot Vacuum-Mop P (viomi.vacuum.v8)",
            name=entry.title,
            sw_version=entry.data.get(CONF_FIRMWARE) or None,
        )
