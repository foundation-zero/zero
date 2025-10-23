from typing import List

from ..types import IOResult
from ..base import ReaderBase
from pathlib import Path


class VittersReader(ReaderBase):
    def read_io_list(self, path: List[Path]) -> IOResult:
        raise NotImplementedError
