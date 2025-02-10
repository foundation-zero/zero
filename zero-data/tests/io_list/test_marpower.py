from pathlib import Path
from typing import List

from io_processing.io_list import IOTopic
from io_processing.io_list.marpower import read_amcs_excel, read_amcs_excel_to_io_topics


def test_marpower_io_excel():
    amcs_df = read_amcs_excel(
        Path(__file__).parent / "../../io_lists/52422003_3210_AMCS IO-List R1.11.xlsx"
    )
    assert amcs_df.shape == (1276, 70)
    assert amcs_df.columns == [
        "Rev.",
        "Deleted",
        "Target Type",
        "Device",
        "Module",
        "Module Type",
        "Terminal",
        "Is Subscribe",
        "Prefix Device",
        "Tag",
        "Cabinet",
        "System",
        "Yard Tag",
        "Description",
        "Parent",
        "Redundant tag",
        "P&ID",
        "Cable ID",
        "Cable Type",
        "Cable Core No.",
        "OPC UA Node ID",
        "OPC UA Publish Interval",
        "Modbus Slave Address",
        "Modbus Data Type",
        "Modbus Address",
        "Modbus Source Type",
        "Modbus Byte Size",
        "Modbus Swap Words",
        "Modbus Lower",
        "Modbus Upper",
        "Range Lower",
        "Range Upper",
        "Unit",
        "Precision",
        "Alert Code",
        "Alert HH",
        "Alert H",
        "Alert L",
        "Alert LL",
        "Alert F",
        "Delay On",
        "Acknowledge Location",
        "Sounding Locations",
        "Alert priority",
        "Intended Operator Response",
        "Category A",
        "Group Alarm",
        "Call GEA on Alert ",
        "Disallow Inhibit",
        "Vdr ID",
        "General Lock Tag",
        "General Lock Operator",
        "General Lock Level",
        "HH Lock Tag",
        "HH Lock Operator",
        "HH Lock Level",
        "H Lock Tag",
        "H Lock Operator",
        "H Lock Level",
        "L Lock Tag",
        "L Lock Operator",
        "L Lock Level",
        "LL Lock Tag",
        "LL Lock Operator",
        "LL Lock Level",
        "Do Not Log",
        "Log To Daily Report",
        "Log to CDP",
        "Workstation",
        "Timestamp",
    ]


def test_marpower_io_values():
    io_values: List[IOTopic] = read_amcs_excel_to_io_topics(
        Path(__file__).parent / "../../io_lists/52422003_3210_AMCS IO-List R1.11.xlsx"
    )
    assert len(io_values) == 56
