from pathlib import Path
from .types import IOResult, Source
from typing import List


def read_io_list(paths: List[Path], type: Source) -> IOResult:
    if type == "marpower":
        from .readers.marpower import MarpowerReader

        return MarpowerReader().read_io_list(paths)
    elif type == "vitters":
        from .readers.vitters import VittersReader

        return VittersReader().read_io_list(paths)
    elif type == "sail_system":
        from .readers.sail_system import SailSystemReader

        return SailSystemReader().read_io_list(paths)
    else:
        raise ValueError(f"Unsupported IOSource type: {type}")
