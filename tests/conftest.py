"""Load the pure modules without needing Home Assistant installed."""
from __future__ import annotations

import enum
import importlib.util
import sys
import types
from pathlib import Path

PKG = "viomi_v8_under_test"
SRC = Path(__file__).resolve().parents[1] / "custom_components" / "viomi_v8"


def _stub_homeassistant() -> None:
    if "homeassistant.const" in sys.modules:
        return
    ha = types.ModuleType("homeassistant")
    const = types.ModuleType("homeassistant.const")

    class Platform(str, enum.Enum):
        VACUUM = "vacuum"
        SENSOR = "sensor"
        SELECT = "select"

    const.Platform = Platform
    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.const"] = const


def load(name: str):
    _stub_homeassistant()
    if PKG not in sys.modules:
        pkg = types.ModuleType(PKG)
        pkg.__path__ = [str(SRC)]
        sys.modules[PKG] = pkg
    full = f"{PKG}.{name}"
    if full in sys.modules:
        return sys.modules[full]
    spec = importlib.util.spec_from_file_location(full, SRC / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[full] = module
    spec.loader.exec_module(module)
    return module
