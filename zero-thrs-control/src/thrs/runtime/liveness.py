import contextlib
from pathlib import Path


class Liveness:
    def __init__(self, liveness_path: str | None):
        self._path = Path(liveness_path) if liveness_path else None

    def signal(self):
        if self._path:
            with contextlib.suppress(OSError):
                self._path.touch()
