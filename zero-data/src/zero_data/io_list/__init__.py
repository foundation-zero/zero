from pathlib import Path

from .types import IOResult, Source


def read_io_list(paths: list[Path], type: Source) -> IOResult:
    if type == "marpower":
        from .readers.marpower import MarpowerReader

        return MarpowerReader().read_io_list(paths)
    elif type == "sail_system":
        from .readers.sail_system import SailSystemReader

        return SailSystemReader().read_io_list(paths)
    else:
        raise ValueError(f"Unsupported IOSource type: {type}")
