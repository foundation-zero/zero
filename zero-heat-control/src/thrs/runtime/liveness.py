import contextlib
from pathlib import Path


class Liveness:
    def __init__(self, liveness_path: Path | None):
        self._path = liveness_path

    def signal(self):
        if self._path:
            with contextlib.suppress(OSError):
                self._path.touch()
