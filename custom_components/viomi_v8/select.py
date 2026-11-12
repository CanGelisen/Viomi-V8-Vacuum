"""Select entities: water level, cleaning mode, mop pattern."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import ViomiV8Client
from .coordinator import ViomiConfigEntry, ViomiV8Coordinator
from .entity import ViomiV8Entity
from .protocol import CLEAN_MODES, MOP_PATTERNS, WATER_LEVELS, ViomiV8Status

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class ViomiSelectDescription(SelectEntityDescription):
    current_fn: Callable[[ViomiV8Status], str | None]
    set_fn: Callable[[ViomiV8Client, str], None]


SELECTS: tuple[ViomiSelectDescription, ...] = (
    ViomiSelectDescription(
        key="water_level",
        translation_key="water_level",
        options=list(WATER_LEVELS),
        current_fn=lambda s: s.water_level,
        set_fn=lambda c, v: c.set_water_level(v),
    ),
    ViomiSelectDescription(
        key="clean_mode",
        translation_key="clean_mode",
        options=list(CLEAN_MODES),
        current_fn=lambda s: s.clean_mode,
        set_fn=lambda c, v: c.set_clean_mode(v),
    ),
    ViomiSelectDescription(
        key="mop_pattern",
        translation_key="mop_pattern",
        options=list(MOP_PATTERNS),
        current_fn=lambda s: s.mop_pattern,
        set_fn=lambda c, v: c.set_mop_pattern(v),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ViomiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(ViomiV8Select(coordinator, d) for d in SELECTS)


class ViomiV8Select(ViomiV8Entity, SelectEntity):
    entity_description: ViomiSelectDescription

    def __init__(
        self, coordinator: ViomiV8Coordinator, description: ViomiSelectDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def current_option(self) -> str | None:
        return self.entity_description.current_fn(self.coordinator.data)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_run(
            self.entity_description.set_fn, self.coordinator.client, option
        )
