from contextlib import nullcontext as assert_does_not_raise
from pathlib import Path

from zero_alert_forwarder.readiness import Readiness


def test_signal_without_path():
    with assert_does_not_raise():
        Readiness(None).signal()


def test_signal_ignores_unwritable_path(tmp_path: Path):
    with assert_does_not_raise():
        Readiness(tmp_path / "does_not_exist" / "ready").signal()


def test_signal_creates_file(tmp_path: Path):
    path = tmp_path / "ready"
    readiness = Readiness(path)
    assert not path.exists()

    readiness.signal()

    assert path.exists()


def test_leftover_file_of_previous_container_is_removed(tmp_path: Path):
    path = tmp_path / "ready"
    path.touch()

    Readiness(path)

    assert not path.exists()
