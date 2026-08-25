from pathlib import Path

from zero_data.io_list import read_io_list

expected_io_columns = [
    "device",
    "tag",
    "yard_tag",
    "target_type",
    "terminal",
    "cabinet",
    "system",
    "description",
    "unit",
    "precision",
    "data_type",
    "mqtt_topic",
    "mqtt_json_path",
]


def test_marpower_amcs_io_excel():
    marpower_io_result = read_io_list(
        [(Path(__file__).parent / "../../io_lists/io-list ~ help ~ totals.xlsx")],
        "marpower",
    )
    assert marpower_io_result.io_list.shape == (13322, 13)
    assert marpower_io_result.io_list.columns == expected_io_columns
    assert len(marpower_io_result.topics) == 687


def test_mocked_io_excel():
    marpower_io_result = read_io_list(
        [(Path(__file__).parent / "../../io_lists/ZERO mocked IO-List.xlsx")],
        "marpower",
    )
    assert marpower_io_result.io_list.shape == (8779, 13)
    assert marpower_io_result.io_list.columns == expected_io_columns
    assert len(marpower_io_result.topics) == 16
