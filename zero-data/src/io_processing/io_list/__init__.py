from pathlib import Path
from .types import IOResult, Source


def read_io_list(path: Path, type: Source) -> IOResult:
    if type == "marpower":
        from .readers.marpower import MarpowerReader

        return MarpowerReader().read_io_list(path)
    elif type == "vitters":
        from .readers.vitters import VittersReader

        return VittersReader().read_io_list(path)
    else:
        raise ValueError(f"Unsupported IOSource type: {type}")
