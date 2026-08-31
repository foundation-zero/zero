from pathlib import Path

from .readers.cached import CachedReader
from .types import IOResult, Source


def read_io_list(
    paths: list[Path],
    type: Source,
    cache_dir: Path | None = None,
) -> IOResult:
    def cache(reader):
        return reader if cache_dir is None else CachedReader(reader, cache_dir)

    if type == "marpower":
        from .readers.marpower import MarpowerReader

        return cache(MarpowerReader()).read_io_list(paths)
    elif type == "sail_system":
        from .readers.sail_system import SailSystemReader

        return cache(SailSystemReader()).read_io_list(paths)
    elif type == "atpx":
        from .readers.atpx import AtpxReader

        return cache(AtpxReader()).read_io_list(paths)
    else:
        raise ValueError(f"Unsupported IOSource type: {type}")
