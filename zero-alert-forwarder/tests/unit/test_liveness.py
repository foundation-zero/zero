import os
from contextlib import nullcontext as assert_does_not_raise
from pathlib import Path

from zero_alert_forwarder.liveness import Liveness


def test_signal_without_path():
    with assert_does_not_raise():
        Liveness(None).signal()


def test_signal_ignores_unwritable_path(tmp_path: Path):
    with assert_does_not_raise():
        Liveness(tmp_path / "does_not_exist" / "liveness").signal()


def test_signal_creates_file(tmp_path: Path):
    path = tmp_path / "liveness"

    Liveness(path).signal()

    assert path.exists()


def test_signal_updates_timestamp(tmp_path: Path):
    path = tmp_path / "liveness"
    path.touch()
    os.utime(path, (0, 0))

    Liveness(path).signal()

    assert path.stat().st_mtime > 0
