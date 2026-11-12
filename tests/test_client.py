import sys
import types

import pytest
from conftest import load


class FakeVacuum:
    """Stands in for miio.ViomiVacuum and records raw commands."""

    sent: list = []
    status_data: dict = {}

    def __init__(self, host, token, timeout=None):
        self.host = host

    def send(self, command, params=None):
        FakeVacuum.sent.append((command, params))
        return ["ok"]

    def find(self):
        FakeVacuum.sent.append(("find", None))

    def status(self):
        return types.SimpleNamespace(data=FakeVacuum.status_data)


@pytest.fixture()
def client(monkeypatch):
    FakeVacuum.sent = []
    FakeVacuum.status_data = {"run_state": 5, "battary_life": 90}
    fake = types.ModuleType("miio")
    fake.ViomiVacuum = FakeVacuum
    monkeypatch.setitem(sys.modules, "miio", fake)
    monkeypatch.setattr(load("client").time, "sleep", lambda _s: None)
    return load("client").ViomiV8Client("1.2.3.4", "0" * 32)


def test_basic_commands(client):
    client.start()
    client.pause()
    client.stop()
    assert FakeVacuum.sent == [
        ("set_mode_withroom", [0, 1, 0]),
        ("set_mode_withroom", [0, 2, 0]),
        ("set_mode", [0]),
    ]


def test_settings_commands(client):
    client.set_fan_speed("turbo")
    client.set_water_level("high")
    client.set_clean_mode("mop")
    client.set_mop_pattern("y_shape")
    assert FakeVacuum.sent == [
        ("set_suction", [3]),
        ("set_suction", [13]),
        ("set_mop", [2]),
        ("set_moproute", [1]),
    ]


def test_return_home_pauses_first_only_when_asked(client):
    client.return_home(pause_first=False)
    assert FakeVacuum.sent == [("set_charge", [1])]
    FakeVacuum.sent.clear()
    client.return_home(pause_first=True)
    assert FakeVacuum.sent == [("set_mode_withroom", [0, 2, 0]), ("set_charge", [1])]


def test_room_clean_and_raw(client):
    client.clean_rooms([10, 13])
    client.send_command("get_prop", ["run_state"])
    assert FakeVacuum.sent == [
        ("set_mode_withroom", [0, 1, 2, 10, 13]),
        ("get_prop", ["run_state"]),
    ]


def test_status_and_empty_status(client):
    assert client.status().activity == "docked"
    FakeVacuum.status_data = {}
    with pytest.raises(ValueError):
        client.status()
