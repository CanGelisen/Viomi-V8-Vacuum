"""Pure protocol helpers for viomi.vacuum.v8 (legacy miIO, not MIoT).

No Home Assistant or python-miio imports here, so this module can be unit
tested on its own.

Command shapes come from python-miio's ViomiVacuum, the homebridge viomi
plugin and community reports for the STYJ02YM:

    start        set_mode_withroom [0, 1, 0]
    pause        set_mode_withroom [0, 2, 0]
    stop         set_mode          [0]
    dock         set_charge        [1]
    fan speed    set_suction       [0..3]
    water level  set_suction       [11..13]
    clean mode   set_mop           [0..2]
    mop pattern  set_moproute      [0|1]
    room clean   set_mode_withroom [edge, 1, n_rooms, *room_ids]
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

# run_state -> activity. 2 is reported as "Idle2" by python-miio; it is shown
# as paused here, which matches how the robot behaves after a pause command.
RUN_STATE_ACTIVITY: dict[int, str] = {
    -1: "idle",
    0: "idle",
    1: "idle",
    2: "paused",
    3: "cleaning",
    4: "returning",
    5: "docked",
}

FAN_SPEEDS: dict[str, int] = {"silent": 0, "standard": 1, "medium": 2, "turbo": 3}
WATER_LEVELS: dict[str, int] = {"low": 11, "medium": 12, "high": 13}
CLEAN_MODES: dict[str, int] = {"vacuum": 0, "vacuum_and_mop": 1, "mop": 2}
MOP_PATTERNS: dict[str, int] = {"s_shape": 0, "y_shape": 1}
BIN_TYPES: dict[int, str] = {
    0: "none",
    1: "dust_bin",
    2: "water_tank",
    3: "dust_bin_and_water_tank",
}

# err_state values that are status messages, not faults.
BENIGN_ERRORS = frozenset({0, 2101, 2103, 2105})
ERROR_TEXT: dict[int, str] = {
    0: "No error",
    500: "Radar timed out",
    501: "Wheels stuck",
    502: "Low battery",
    503: "Dust bin missing",
    508: "Uneven ground",
    521: "Water tank is not installed",
    522: "Mop is not installed",
    525: "Insufficient water in water tank",
    527: "Remove mop",
    528: "Dust bin missing",
    529: "Mop and water tank missing",
    530: "Mop and water tank missing",
    531: "Water tank is not installed",
    2101: "Insufficient battery, continuing cleaning after recharge",
    2103: "Charging",
    2105: "Fully charged",
}


@dataclass(frozen=True)
class ViomiV8Status:
    """Parsed vacuum state."""

    activity: str
    run_state: int | None
    battery: int | None
    error_code: int | None
    error_text: str | None
    fan_speed: str | None
    water_level: str | None
    clean_mode: str | None
    mop_pattern: str | None
    bin_type: str | None
    clean_area: float | None
    clean_time: int | None  # minutes
    has_map: bool | None


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _name_for(table: Mapping[str, int], value: int | None) -> str | None:
    for name, raw in table.items():
        if raw == value:
            return name
    return None


def parse_status(data: Mapping[str, Any]) -> ViomiV8Status:
    """Turn the raw get_prop dictionary into a ViomiV8Status."""
    run_state = _to_int(data.get("run_state"))
    error = _to_int(data.get("err_state"))
    has_fault = error is not None and error not in BENIGN_ERRORS
    activity = "error" if has_fault else RUN_STATE_ACTIVITY.get(run_state, "idle")

    has_map = _to_int(data.get("has_map"))
    return ViomiV8Status(
        activity=activity,
        run_state=run_state,
        battery=_to_int(data.get("battary_life")),  # sic: the device spells it so
        error_code=error,
        error_text=None if error is None else ERROR_TEXT.get(error, f"Error {error}"),
        fan_speed=_name_for(FAN_SPEEDS, _to_int(data.get("suction_grade"))),
        water_level=_name_for(WATER_LEVELS, _to_int(data.get("water_grade"))),
        clean_mode=_name_for(CLEAN_MODES, _to_int(data.get("is_mop"))),
        mop_pattern=_name_for(MOP_PATTERNS, _to_int(data.get("mop_type"))),
        bin_type=BIN_TYPES.get(_to_int(data.get("box_type"))),
        clean_area=_to_float(data.get("s_area")),
        clean_time=_to_int(data.get("s_time")),
        has_map=None if has_map is None else bool(has_map),
    )


def room_clean_params(rooms: list[int], edge: bool = False) -> list[int]:
    """Parameters for set_mode_withroom to clean specific rooms."""
    if not rooms:
        raise ValueError("at least one room id is required")
    if any((not isinstance(r, int)) or r < 0 for r in rooms):
        raise ValueError("room ids must be non-negative integers")
    return [1 if edge else 0, 1, len(rooms), *rooms]
