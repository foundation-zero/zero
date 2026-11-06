from pathlib import Path
from typing import NoReturn

import pytest

from zero_modbus_bridge.readiness import Readiness


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


@pytest.fixture
def status_file(tmp_path: Path) -> Path:
    return tmp_path / "readiness"


@pytest.fixture
def readiness(status_file: Path, clock: FakeClock) -> Readiness:
    return Readiness(status_file, 900, clock=clock, exit_process=_exit)


def test_no_status_file_until_first_report(readiness: Readiness, status_file: Path):
    assert not status_file.exists()


def test_ready(readiness: Readiness, status_file: Path):
    readiness.ready("mqtt")
    assert status_file.read_text() == "ready\n"


def test_not_ready_names_each_dependency(readiness: Readiness, status_file: Path):
    readiness.not_ready("mqtt", "CONNACK refused (return code 135)")
    readiness.not_ready("modbus", "gateway unreachable")

    status = status_file.read_text()
    assert status.startswith("not ready since ")
    assert status.endswith(
        ": mqtt: CONNACK refused (return code 135); modbus: gateway unreachable\n"
    )


def test_ready_only_when_every_dependency_is(readiness: Readiness, status_file: Path):
    readiness.not_ready("mqtt", "down")
    readiness.not_ready("modbus", "down")
    readiness.ready("mqtt")
    assert status_file.read_text().endswith(": modbus: down\n")

    readiness.ready("modbus")
    assert status_file.read_text() == "ready\n"


def test_exits_after_deadline(readiness: Readiness, clock: FakeClock):
    readiness.not_ready("mqtt", "down")
    clock.now = 899
    readiness.not_ready("mqtt", "still down")

    clock.now = 900
    with pytest.raises(
        Exited, match=r"^not ready for 15 min \(not ready since .*: mqtt: still down\)$"
    ):
        readiness.not_ready("mqtt", "still down")


def test_deadline_restarts_after_being_ready(readiness: Readiness, clock: FakeClock):
    readiness.not_ready("mqtt", "down")
    clock.now = 800
    readiness.ready("mqtt")
    readiness.not_ready("mqtt", "down again")

    clock.now = 1600
    readiness.not_ready("mqtt", "down again")  # 800 s since it went down again


def test_without_status_file(clock: FakeClock):
    readiness = Readiness(None, clock=clock, exit_process=_exit)
    readiness.not_ready("mqtt", "down")
    assert readiness.status.endswith(": mqtt: down")
