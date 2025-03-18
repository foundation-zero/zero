from abc import ABC, abstractmethod
from pathlib import Path
from .types import IOResult


class ReaderBase(ABC):
    @abstractmethod
    def read_io_list(self, path: Path) -> IOResult: ...

    @staticmethod
    def convert_value(val):
        if val is None:
            return None
        elif isinstance(val, str):
            return val
        elif int(val) == val:
            return str(int(val))
        else:
            return str(val)
