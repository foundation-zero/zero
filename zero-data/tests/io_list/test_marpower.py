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
                / "../../io_lists/52422003_3210_AMCS IO-List R2.29_PvK_MQTT.xlsx"
            )
        ],
        "marpower",
    )
    assert marpower_io_result.io_list.shape == (5706, 13)
    assert marpower_io_result.io_list.columns == expected_io_columns
    assert len(marpower_io_result.topics) == 562


def test_marpower_pms_io_excel():
    marpower_io_result = read_io_list(
        [
            (
                Path(__file__).parent
                / "../../io_lists/52422003_3211_PMS IO-List R2.12-fixed2.xlsx"
            )
        ],
        "marpower",
    )
    assert marpower_io_result.io_list.shape == (11522, 13)
    assert marpower_io_result.io_list.columns == expected_io_columns
    assert len(marpower_io_result.topics) == 850


def test_mocked_io_excel():
    marpower_io_result = read_io_list(
        [(Path(__file__).parent / "../../io_lists/ZERO mocked IO-List.xlsx")],
        "marpower",
    )
    assert marpower_io_result.io_list.shape == (8977, 13)
    assert marpower_io_result.io_list.columns == expected_io_columns
    assert len(marpower_io_result.topics) == 11
