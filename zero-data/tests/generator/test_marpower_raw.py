from pathlib import Path, PosixPath
from unittest.mock import patch, mock_open

import io_processing.generator.marpower_raw
from io_processing.io_list import IOTopic, IOValue


def test_marpower_raw():
    marpower_io_topics = [
        IOTopic("test_topic", [IOValue("field1", "bool"), IOValue("field2", "f32")])
    ]
    open_mock = mock_open()
    with patch("io_processing.generator.marpower_raw.open", open_mock, create=True):
        io_processing.generator.marpower_raw.MarpowerRawGenerator(
            Path("/not-used"), marpower_io_topics
        ).generate()
        open_mock.assert_called_with(
            PosixPath("/not-used/models/raw/marpower/test_topic.sql"), "w"
        )
