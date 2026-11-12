"""Sensors for the Viomi V8."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfArea, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import ViomiConfigEntry, ViomiV8Coordinator
from .entity import ViomiV8Entity
from .protocol import BIN_TYPES, ViomiV8Status


@dataclass(frozen=True, kw_only=True)
class ViomiSensorDescription(SensorEntityDescription):
    value_fn: Callable[[ViomiV8Status], StateType]


SENSORS: tuple[ViomiSensorDescription, ...] = (
    ViomiSensorDescription(
        key="battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.battery,
    ),
    ViomiSensorDescription(
        key="clean_area",
        translation_key="clean_area",
        native_unit_of_measurement=UnitOfArea.SQUARE_METERS,
        device_class=SensorDeviceClass.AREA,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.clean_area,
    ),
    ViomiSensorDescription(
        key="clean_time",
        translation_key="clean_time",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.clean_time,
    ),
    ViomiSensorDescription(
        key="error",
        translation_key="error",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.error_text,
    ),
    ViomiSensorDescription(
        key="attachment",
        translation_key="attachment",
        device_class=SensorDeviceClass.ENUM,
        options=list(BIN_TYPES.values()),
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.bin_type,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ViomiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(ViomiV8Sensor(coordinator, d) for d in SENSORS)


class ViomiV8Sensor(ViomiV8Entity, SensorEntity):
    entity_description: ViomiSensorDescription

    def __init__(
        self, coordinator: ViomiV8Coordinator, description: ViomiSensorDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        return self.entity_description.value_fn(self.coordinator.data)
