from pathlib import Path, PosixPath
from unittest.mock import patch, mock_open

from io_processing.dbt_gen.marpower_raw import MarpowerRawGenerator
from io_processing.io_list.types import IOTopic, IOValue


def test_marpower_raw():
    marpower_io_topics = [
        IOTopic("test_topic", [IOValue("field1", "bool"), IOValue("field2", "f32")])
    ]
    open_mock = mock_open()
    with patch("io_processing.dbt_gen.marpower_raw.open", open_mock, create=True):
        MarpowerRawGenerator(Path("/not-used")).generate(marpower_io_topics)
        open_mock.assert_called_with(
            PosixPath("/not-used/models/raw/marpower/test_topic.sql"), "w"
        )
