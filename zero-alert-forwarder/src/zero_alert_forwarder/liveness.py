import contextlib
from pathlib import Path


class Liveness:
    """Touches a file for Kubernetes to check the age of, as a sign the polling loop still runs."""

    def __init__(self, liveness_path: Path | None):
        self._path = liveness_path

    def signal(self):
        if self._path:
            with contextlib.suppress(OSError):
                self._path.touch()
