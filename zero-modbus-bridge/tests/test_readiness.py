import re
from pathlib import Path
from typing import NoReturn

import pytest

from zero_modbus_bridge import readiness as readiness_module
from zero_modbus_bridge.readiness import Readiness, exit_with_reason


class Exited(Exception):
    pass


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def _exit(reason: str) -> NoReturn:
    raise Exited(reason)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


SINCE = r"since \d\d:\d\d:\d\d UTC"


@pytest.fixture
def status_file(tmp_path: Path) -> Path:
    return tmp_path / "ready"


@pytest.fixture
def readiness(status_file: Path, clock: FakeClock) -> Readiness:
    return Readiness(
        status_file,
        {"mqtt": "connecting", "modbus": "not probed yet"},
        900,
        clock=clock,
        exit_process=_exit,
    )


def test_starts_not_ready(readiness: Readiness, status_file: Path):
    assert re.fullmatch(
        f"not ready: mqtt: connecting; modbus: not probed yet {SINCE}\n",
        status_file.read_text(),
    )


def test_replaces_a_stale_status_file(status_file: Path, clock: FakeClock):
    status_file.write_text("ready: mqtt since 12:00:00 UTC\n")
    Readiness(status_file, {"mqtt": "connecting"}, clock=clock, exit_process=_exit)
    assert status_file.read_text().startswith("not ready: mqtt: connecting")


def test_ready_once_every_dependency_is(readiness: Readiness, status_file: Path):
    readiness.ready("mqtt")
    assert re.fullmatch(
        f"not ready: modbus: not probed yet {SINCE}\n", status_file.read_text()
    )

    readiness.ready("modbus")
    assert re.fullmatch(f"ready: mqtt, modbus {SINCE}\n", status_file.read_text())


def test_not_ready_names_each_dependency(readiness: Readiness, status_file: Path):
    readiness.not_ready("mqtt", "CONNACK refused (return code 135)")
    readiness.not_ready("modbus", "gateway unreachable")

    assert re.fullmatch(
        "not ready: mqtt: CONNACK refused \\(return code 135\\); "
        f"modbus: gateway unreachable {SINCE}\n",
        status_file.read_text(),
    )


def test_exits_after_deadline(readiness: Readiness, clock: FakeClock):
    clock.now = 899
    readiness.not_ready("mqtt", "down")

    clock.now = 900
    with pytest.raises(
        Exited,
        match=r"^not ready for 15 min \(not ready: mqtt: down; modbus: .* UTC\)$",
    ):
        readiness.not_ready("mqtt", "down")


def test_deadline_restarts_after_being_ready(readiness: Readiness, clock: FakeClock):
    clock.now = 800
    readiness.ready("mqtt")
    readiness.ready("modbus")
    readiness.not_ready("mqtt", "down")

    clock.now = 1600
    readiness.not_ready("mqtt", "down")  # 800 s since it went down again


def test_without_status_file(clock: FakeClock):
    readiness = Readiness(None, {"mqtt": "connecting"}, clock=clock, exit_process=_exit)
    readiness.ready("mqtt")
    assert readiness.status.startswith("ready: mqtt since ")


@pytest.fixture
def exit_code(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    codes: list[int] = []

    def fake_exit(code: int) -> NoReturn:
        codes.append(code)
        raise Exited()

    monkeypatch.setattr(readiness_module.os, "_exit", fake_exit)
    return codes


def test_exit_writes_termination_message(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, exit_code: list[int]
):
    termination_log = tmp_path / "termination-log"
    monkeypatch.setattr(readiness_module, "TERMINATION_LOG", termination_log)

    with pytest.raises(Exited):
        exit_with_reason("mqtt: gave up")

    assert termination_log.read_text() == "mqtt: gave up"
    assert exit_code == [1]


def test_exit_without_termination_log(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, exit_code: list[int]
):
    monkeypatch.setattr(readiness_module, "TERMINATION_LOG", tmp_path / "no" / "log")

    with pytest.raises(Exited):
        exit_with_reason("mqtt: gave up")

    assert exit_code == [1]
