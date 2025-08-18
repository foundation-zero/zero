from pathlib import Path, PosixPath
from unittest.mock import patch, mock_open, MagicMock

from zero_data.dbt_gen.marpower_raw import MarpowerRawGenerator
from zero_data.io_list.types import IOTopic, IOValue


def test_marpower_raw():
    marpower_io_topics = [
        IOTopic("test_topic", [IOValue("field1", "bool"), IOValue("field2", "f32")])
    ]
    open_mock = mock_open()
    mkdir_mock = MagicMock()
    with (
        patch("zero_data.dbt_gen.marpower_raw.open", open_mock, create=True),
        patch("pathlib.Path.mkdir", mkdir_mock),
    ):
        MarpowerRawGenerator(Path("/not-used")).generate(marpower_io_topics)
        mkdir_mock.assert_called_with(parents=True, exist_ok=True)
        open_mock.assert_any_call(
            PosixPath("/not-used/models/00_source/marpower/test_topic.sql"), "w"
        )
        open_mock.assert_any_call(
            PosixPath("/not-used/models/40_sinks/marpower/test_topic_sink.sql"), "w"
        )
