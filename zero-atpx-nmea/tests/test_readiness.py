from pathlib import Path
from typing import NoReturn

import pytest

from zero_atpx_nmea import readiness as readiness_module
from zero_atpx_nmea.readiness import Readiness, exit_with_reason


class Exited(Exception):
    pass


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def fake_exit(reason: str) -> NoReturn:
    raise Exited(reason)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def status_file(tmp_path: Path) -> Path:
    return tmp_path / "ready"


@pytest.fixture
def readiness(status_file: Path, clock: FakeClock) -> Readiness:
    return Readiness(
        status_file, ["atpx-mqtt", "mqtt"], 900, clock=clock, exit_process=fake_exit
    )


def test_starts_not_ready_on_every_dependency(readiness: Readiness, status_file: Path):
    status = status_file.read_text()
    assert status.startswith(
        "not ready: atpx-mqtt: connecting; mqtt: connecting since "
    )
    assert status.endswith(" UTC\n")


def test_ready_once_every_dependency_is(readiness: Readiness, status_file: Path):
    readiness.ready("mqtt", "connected")
    assert status_file.read_text().startswith("not ready: atpx-mqtt: connecting since ")

    readiness.ready("atpx-mqtt", "connected")
    assert status_file.read_text().startswith(
        "ready: atpx-mqtt: connected; mqtt: connected since "
    )


def test_not_ready_names_only_the_dependency_that_is_down(
    readiness: Readiness, status_file: Path
):
    readiness.ready("atpx-mqtt", "connected")
    readiness.ready("mqtt", "connected")
    readiness.not_ready("atpx-mqtt", "ConnectionRefusedError: refused")
    assert status_file.read_text().startswith(
        "not ready: atpx-mqtt: ConnectionRefusedError: refused since "
    )


def test_exits_after_deadline(readiness: Readiness, clock: FakeClock):
    clock.now = 899
    readiness.not_ready("mqtt", "still down")

    clock.now = 900
    with pytest.raises(
        Exited,
        match=r"^not ready for 15 min \(not ready: atpx-mqtt: connecting; "
        r"mqtt: still down since \d\d:\d\d:\d\d UTC\)$",
    ):
        readiness.not_ready("mqtt", "still down")


def test_deadline_restarts_after_being_ready(readiness: Readiness, clock: FakeClock):
    clock.now = 800
    readiness.ready("atpx-mqtt", "connected")
    readiness.ready("mqtt", "connected")
    readiness.not_ready("mqtt", "down again")

    clock.now = 1600
    readiness.not_ready("mqtt", "down again")  # 800 s since it went down again


def test_unwritable_status_file_is_logged(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    readiness = Readiness(tmp_path / "missing" / "ready", ["mqtt"])
    assert "Failed to write readiness" in caplog.text
    assert readiness.status.startswith("not ready: mqtt: connecting since ")


def test_failed_write_is_retried_on_the_next_report(tmp_path: Path):
    status_file = tmp_path / "missing" / "ready"
    readiness = Readiness(status_file, ["mqtt"])
    status_file.parent.mkdir()

    readiness.not_ready("mqtt", "connecting")
    assert status_file.read_text().startswith("not ready: mqtt: connecting since ")


@pytest.fixture
def exit_code(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    codes: list[int] = []

    def fake_os_exit(code: int) -> NoReturn:
        codes.append(code)
        raise Exited()

    monkeypatch.setattr(readiness_module.os, "_exit", fake_os_exit)
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
