import hashlib
import json
import pickle
from pathlib import Path

import polars as pl

from ..base import ReaderBase
from ..types import IOResult

# mtime + size is enough to detect a changed file cheaply without re-reading it.
_Signature = tuple[str, int, int]


def _file_signature(path: Path) -> _Signature:
    stat = path.stat()
    return (str(path), stat.st_mtime_ns, stat.st_size)


class CachedReader(ReaderBase):
    """Cache the result of a wrapped reader on the filesystem.

    The cache key is derived from the source files' mtime and size, so the
    underlying reader is only invoked again when a source file changes.
    """

    def __init__(self, reader: ReaderBase, cache_dir: Path):
        self._reader = reader
        self._cache_dir = cache_dir

    @staticmethod
    def _cache_key(paths: list[Path]) -> str:
        manifest = [_file_signature(path) for path in paths]
        digest = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()
        ).hexdigest()
        return digest

    def _cache_files(self, paths: list[Path]) -> tuple[Path, Path]:
        key = self._cache_key(paths)
        return (
            self._cache_dir / f"{key}.parquet",
            self._cache_dir / f"{key}.pkl",
        )

    def read_io_list(self, paths: list[Path]) -> IOResult:
        parquet_path, topics_path = self._cache_files(paths)

        if parquet_path.is_file() and topics_path.is_file():
            io_list = pl.read_parquet(parquet_path)
            with topics_path.open("rb") as handle:
                topics = pickle.load(handle)
            return IOResult(io_list, topics)

        result = self._reader.read_io_list(paths)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        result.io_list.write_parquet(parquet_path)
        with topics_path.open("wb") as handle:
            pickle.dump(result.topics, handle)
        return result
