"""Vacuum entity for the Viomi V8."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_EDGE, ATTR_ROOMS, SERVICE_CLEAN_ROOMS
from .coordinator import ViomiConfigEntry, ViomiV8Coordinator
from .entity import ViomiV8Entity
from .protocol import FAN_SPEEDS

PARALLEL_UPDATES = 1

_ACTIVITY = {
    "cleaning": VacuumActivity.CLEANING,
    "paused": VacuumActivity.PAUSED,
    "idle": VacuumActivity.IDLE,
    "returning": VacuumActivity.RETURNING,
    "docked": VacuumActivity.DOCKED,
    "error": VacuumActivity.ERROR,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ViomiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([ViomiV8Vacuum(entry.runtime_data)])

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_CLEAN_ROOMS,
        {
            vol.Required(ATTR_ROOMS): vol.All(
                cv.ensure_list,
                [vol.All(vol.Coerce(int), vol.Range(min=0))],
                vol.Length(min=1),
            ),
            vol.Optional(ATTR_EDGE, default=False): cv.boolean,
        },
        "async_clean_rooms",
    )


class ViomiV8Vacuum(ViomiV8Entity, StateVacuumEntity):
    """The vacuum itself."""

    _attr_name = None
    _attr_supported_features = (
        VacuumEntityFeature.START
        | VacuumEntityFeature.PAUSE
        | VacuumEntityFeature.STOP
        | VacuumEntityFeature.RETURN_HOME
        | VacuumEntityFeature.LOCATE
        | VacuumEntityFeature.FAN_SPEED
        | VacuumEntityFeature.SEND_COMMAND
        | VacuumEntityFeature.STATE
    )
    _attr_fan_speed_list = list(FAN_SPEEDS)

    def __init__(self, coordinator: ViomiV8Coordinator) -> None:
        super().__init__(coordinator, "vacuum")

    @property
    def activity(self) -> VacuumActivity | None:
        return _ACTIVITY.get(self.coordinator.data.activity)

    @property
    def fan_speed(self) -> str | None:
        return self.coordinator.data.fan_speed

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        return {
            "error_code": data.error_code,
            "error": data.error_text,
            "has_map": data.has_map,
        }

    async def async_start(self) -> None:
        await self.coordinator.async_run(self.coordinator.client.start)

    async def async_pause(self) -> None:
        await self.coordinator.async_run(self.coordinator.client.pause)

    async def async_stop(self, **kwargs: Any) -> None:
        await self.coordinator.async_run(self.coordinator.client.stop)

    async def async_return_to_base(self, **kwargs: Any) -> None:
        cleaning = self.coordinator.data.activity == "cleaning"
        await self.coordinator.async_run(self.coordinator.client.return_home, cleaning)

    async def async_locate(self, **kwargs: Any) -> None:
        await self.coordinator.async_run(self.coordinator.client.locate)

    async def async_set_fan_speed(self, fan_speed: str, **kwargs: Any) -> None:
        await self.coordinator.async_run(self.coordinator.client.set_fan_speed, fan_speed)

    async def async_send_command(
        self, command: str, params: dict[str, Any] | list[Any] | None = None, **kwargs: Any
    ) -> None:
        await self.coordinator.async_run(
            self.coordinator.client.send_command,
            command,
            params if isinstance(params, list) else None,
        )

    async def async_clean_rooms(self, rooms: list[int], edge: bool = False) -> None:
        """Clean specific rooms by their device room id."""
        await self.coordinator.async_run(self.coordinator.client.clean_rooms, rooms, edge)
