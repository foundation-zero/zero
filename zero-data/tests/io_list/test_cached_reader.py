import pickle
from pathlib import Path

import polars as pl
import pytest

from zero_data.io_list.base import ReaderBase
from zero_data.io_list.readers.cached import CachedReader
from zero_data.io_list.types import IOResult, IOTopic, IOValue


class SpyReader(ReaderBase):
    """Reader that counts how many times read_io_list is actually called."""

    def __init__(self):
        self.calls = 0

    def read_io_list(self, paths: list[Path]) -> IOResult:
        self.calls += 1
        df = pl.DataFrame({"tag": ["a", "b"]})
        topics = [IOTopic("telemetry/a", [IOValue("a", "REAL")])]
        return IOResult(df, topics)


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    path = tmp_path / "source.txt"
    path.write_text("hello")
    return path


def test_reads_underlying_reader_and_seed_cache(
    tmp_path: Path, source_file: Path
) -> None:
    reader = SpyReader()
    cached = CachedReader(reader, tmp_path / "cache")
    result = cached.read_io_list([source_file])

    assert reader.calls == 1
    assert result.io_list.columns == ["tag"]
    assert result.topics[0].topic == "telemetry/a"
    assert (tmp_path / "cache").is_dir()
    assert list((tmp_path / "cache").iterdir())


def test_serves_from_cache_without_calling_reader(
    tmp_path: Path, source_file: Path
) -> None:
    reader = SpyReader()
    cached = CachedReader(reader, tmp_path / "cache")

    first = cached.read_io_list([source_file])
    second = cached.read_io_list([source_file])

    assert reader.calls == 1
    assert first.io_list.equals(second.io_list)
    assert first.topics == second.topics


def test_recaches_when_source_file_changes(tmp_path: Path, source_file: Path) -> None:
    reader = SpyReader()
    cached = CachedReader(reader, tmp_path / "cache")

    cached.read_io_list([source_file])
    assert reader.calls == 1

    source_file.write_text("changed")
    cached.read_io_list([source_file])
    assert reader.calls == 2


def test_topics_are_stored_as_pickle(tmp_path: Path, source_file: Path) -> None:
    reader = SpyReader()
    cached = CachedReader(reader, tmp_path / "cache")

    cached.read_io_list([source_file])
    topics_path = next((tmp_path / "cache").glob("*.pkl"))
    with topics_path.open("rb") as handle:
        stored = pickle.load(handle)

    assert stored == [IOTopic("telemetry/a", [IOValue("a", "REAL")])]
