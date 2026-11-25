import contextlib
from pathlib import Path


class Readiness:
    """Creates a file once polling is set up, so Kubernetes only replaces the old pod after that."""

    def __init__(self, readiness_path: Path | None):
        self._path = readiness_path
        if readiness_path:
            # The emptyDir outlives container restarts, so a leftover file would claim readiness too early.
            with contextlib.suppress(OSError):
                readiness_path.unlink(missing_ok=True)

    def signal(self):
        if self._path:
            with contextlib.suppress(OSError):
                self._path.touch()
