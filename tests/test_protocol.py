import pytest
from conftest import load

protocol = load("protocol")

# Sample get_prop result for a docked, charging v8 (from python-miio's docs).
DOCKED = {
    "run_state": 5, "mode": 0, "err_state": 2103, "battary_life": 85,
    "box_type": 3, "mop_type": 1, "s_time": 0, "s_area": 0,
    "suction_grade": 1, "water_grade": 11, "remember_map": 1,
    "has_map": 1, "is_mop": 1, "has_newmap": 0,
}


def test_docked_status():
    s = protocol.parse_status(DOCKED)
    assert s.activity == "docked"
    assert s.battery == 85
    assert s.fan_speed == "standard"
    assert s.water_level == "low"
    assert s.clean_mode == "vacuum_and_mop"
    assert s.mop_pattern == "y_shape"
    assert s.bin_type == "dust_bin_and_water_tank"
    assert s.error_text == "Charging"
    assert s.has_map is True


def test_cleaning_status():
    s = protocol.parse_status({**DOCKED, "run_state": 3, "err_state": 0, "s_time": 12, "s_area": 8.5})
    assert s.activity == "cleaning"
    assert s.clean_time == 12
    assert s.clean_area == 8.5


@pytest.mark.parametrize("code,text", [(501, "Wheels stuck"), (999, "Error 999")])
def test_fault_becomes_error_activity(code, text):
    s = protocol.parse_status({**DOCKED, "err_state": code})
    assert s.activity == "error"
    assert s.error_text == text


def test_unknown_and_missing_values_do_not_crash():
    s = protocol.parse_status({"run_state": "x", "suction_grade": 99, "water_grade": None})
    assert s.activity == "idle"
    assert s.fan_speed is None and s.water_level is None and s.battery is None


def test_room_clean_params_match_known_working_shape():
    # Community-verified on a v8: set_mode_withroom[0, 1, 1, 13] cleans room 13.
    assert protocol.room_clean_params([13]) == [0, 1, 1, 13]
    assert protocol.room_clean_params([10, 13], edge=True) == [1, 1, 2, 10, 13]


@pytest.mark.parametrize("bad", [[], [-1], ["a"]])
def test_room_clean_params_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        protocol.room_clean_params(bad)
