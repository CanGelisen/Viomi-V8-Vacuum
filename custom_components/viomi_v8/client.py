"""Blocking miIO client for viomi.vacuum.v8. Run it in an executor."""
from __future__ import annotations

import threading
import time
from typing import Any

from .const import REQUEST_TIMEOUT
from .protocol import (
    CLEAN_MODES,
    FAN_SPEEDS,
    MOP_PATTERNS,
    WATER_LEVELS,
    ViomiV8Status,
    parse_status,
    room_clean_params,
)


class ViomiV8Client:
    """Thin wrapper over python-miio's ViomiVacuum.

    A lock serialises every request: the miIO protocol is a single UDP
    conversation and does not tolerate overlapping calls.
    """

    def __init__(self, host: str, token: str, timeout: int = REQUEST_TIMEOUT) -> None:
        from miio import ViomiVacuum

        self._dev = ViomiVacuum(host, token, timeout=timeout)
        self._lock = threading.Lock()

    # --- reads -----------------------------------------------------------
    def info(self) -> Any:
        with self._lock:
            return self._dev.info()

    def status(self) -> ViomiV8Status:
        with self._lock:
            data = self._dev.status().data
        if data.get("run_state") is None and data.get("battary_life") is None:
            raise ValueError("vacuum returned an empty status")
        return parse_status(data)

    # --- commands --------------------------------------------------------
    def start(self) -> None:
        self._send("set_mode_withroom", [0, 1, 0])

    def pause(self) -> None:
        self._send("set_mode_withroom", [0, 2, 0])

    def stop(self) -> None:
        self._send("set_mode", [0])

    def return_home(self, pause_first: bool = False) -> None:
        # While cleaning the robot ignores a plain dock command; pausing first
        # is what the homebridge viomi plugin does.
        with self._lock:
            if pause_first:
                self._dev.send("set_mode_withroom", [0, 2, 0])
                time.sleep(1)
            self._dev.send("set_charge", [1])

    def locate(self) -> None:
        with self._lock:
            self._dev.find()

    def set_fan_speed(self, name: str) -> None:
        self._send("set_suction", [FAN_SPEEDS[name]])

    def set_water_level(self, name: str) -> None:
        # The device takes water levels (11-13) on the same command as fan speed.
        self._send("set_suction", [WATER_LEVELS[name]])

    def set_clean_mode(self, name: str) -> None:
        self._send("set_mop", [CLEAN_MODES[name]])

    def set_mop_pattern(self, name: str) -> None:
        self._send("set_moproute", [MOP_PATTERNS[name]])

    def clean_rooms(self, rooms: list[int], edge: bool = False) -> None:
        self._send("set_mode_withroom", room_clean_params(rooms, edge))

    def send_command(self, command: str, params: list | None = None) -> Any:
        return self._send(command, params or [])

    def _send(self, command: str, params: list) -> Any:
        with self._lock:
            return self._dev.send(command, params)
