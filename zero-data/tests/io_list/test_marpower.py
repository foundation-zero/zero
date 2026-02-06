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


def test_marpower_amcs_io_excel(marpower_io_result):
    marpower_io_result = read_io_list(
        [
            (
                Path(__file__).parent
                / "../../io_lists/52422003_3210_AMCS IO-List R2.22-MQTT-fix.xlsx"
            )
        ],
        "marpower",
    )
    assert marpower_io_result.io_list.shape == (4221, 13)
    assert marpower_io_result.io_list.columns == expected_io_columns
    assert len(marpower_io_result.topics) == 296


def test_marpower_pms_io_excel():
    marpower_io_result = read_io_list(
        [
            (
                Path(__file__).parent
                / "../../io_lists/52422003_3211_PMS IO-List R2.10-MQTT-fix.xlsx"
            )
        ],
        "marpower",
    )
    assert marpower_io_result.io_list.shape == (11522, 13)
    assert marpower_io_result.io_list.columns == expected_io_columns
    assert len(marpower_io_result.topics) == 849


def test_mocked_io_excel():
    marpower_io_result = read_io_list(
        [(Path(__file__).parent / "../../io_lists/ZERO mocked IO-List.xlsx")],
        "marpower",
    )
    assert marpower_io_result.io_list.shape == (9582, 13)
    assert marpower_io_result.io_list.columns == expected_io_columns
    assert len(marpower_io_result.topics) == 132
