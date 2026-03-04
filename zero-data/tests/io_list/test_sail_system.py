from pathlib import Path

import pytest

from zero_data.io_list.readers.sail_system import SailSystemReader
from zero_data.io_list.types import IOTopic, IOValue


@pytest.fixture
def get_test_file_path():
    def _do(case_name):
        return Path(__file__).parent / f"../../io_lists/test/sailsystem_{case_name}.xml"

    return _do


def test_read_io_list(get_test_file_path):
    test_path = get_test_file_path("happy")
    coolingpumps_data_type = (
        "STRUCT<x_ExtOnOff BOOLEAN, i_State INTEGER, "
        "ui_RunningHours INTEGER, i_Temperature "
        "INTEGER>"
    )
    expected_topics = [
        IOTopic(
            topic="sail-systems/coolingpumps",
            fields=[
                IOValue(
                    name="sFrpk",
                    data_type=coolingpumps_data_type,
                ),
                IOValue(
                    name="sHlyrdpt",
                    data_type=coolingpumps_data_type,
                ),
                IOValue(
                    name="sTchSpc",
                    data_type=coolingpumps_data_type,
                ),
                IOValue(
                    name="sLzrtt",
                    data_type=coolingpumps_data_type,
                ),
                IOValue(name="iDelayTime", data_type="INTEGER"),
            ],
            group="T_sCooling",
        )
    ]
    result = SailSystemReader().read_io_list([test_path])
    assert result.io_list.is_empty()
    assert result.topics == expected_topics


def test_no_hmi_node(get_test_file_path):
    test_path = get_test_file_path("no_hmi_node")

    with pytest.raises(
        ValueError, match=f"No Application/HmiData node found in {test_path}"
    ):
        SailSystemReader().read_io_list([test_path])
