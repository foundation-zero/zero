import pytest

from loads.registry.sheets import (
    IoListLabel,
    io_list_labels,
    io_list_topics_without_variable,
    max_loads_problems,
    unknown_technical_names,
)

IO_LIST_HEADER = (
    "Issued,14/07/2026,,,\n"
    'Type,Topic,Display name,"Abbreviated\n display name",Display units\n'
)

MAX_LOADS_HEADER = (
    ",,Alarms,,,\n"
    "Loads app technical name,Lower Warning Setting (kg),Lower Alarm Setting (kg),"
    "Upper Warning Setting (kg),Upper Alarm Setting (kg)\n"
)


def test_unknown_technical_names_skips_the_header_rows_and_blank_names():
    csv_text = (
        "Loads app technical name,Note\n"
        "main-sheet-load,\n"
        ",a row without a technical name\n"
        "main-sheet-lod,\n"
    )

    assert unknown_technical_names(csv_text, header_rows=1) == {"main-sheet-lod"}


def test_io_list_labels_join_on_topic_regardless_of_case():
    io_list_csv = (
        IO_LIST_HEADER
        + "InputReg,F0103_BladeAdjuster.st_load.i_Load,Blade RTA Load,B RTA,t\n"
        + "InputReg,F0103_BladeAdjuster.st_position.i_Unknown,,,\n"
    )

    assert io_list_labels(io_list_csv) == {
        "blade-adjuster-load": IoListLabel(
            display_name="Blade RTA Load",
            abbreviated_display_name="B RTA",
            display_units="t",
        )
    }


def test_io_list_topics_without_variable_lists_labelled_topics_outside_the_registry():
    io_list_csv = (
        IO_LIST_HEADER
        + "InputReg,F0103_BladeAdjuster.st_load.i_Load,Blade RTA Load,B RTA,t\n"
        + "InputReg,F9999_Unknown.i_Load,Unknown Load,UNK,t\n"
        + "InputReg,F9998_Unlabelled.i_Load,,,\n"
    )

    assert io_list_topics_without_variable(io_list_csv) == ["F9999_Unknown.i_Load"]


@pytest.mark.parametrize(
    ("row", "problem"),
    [
        ('main-sheet-load,,,"11,000","12,000"\n', None),
        ("main-sheet-load,,,???,n/a\n", None),
        ("main-sheet-load,,,11 t,12000\n", "non-numeric warning_high"),
        ('main-sheet-load,,,"13,000","12,000"\n', "Upper warning above upper alarm"),
    ],
)
def test_max_loads_problems(row: str, problem: str | None):
    problems = max_loads_problems(MAX_LOADS_HEADER + row)

    if problem is None:
        assert problems == []
    else:
        assert any(problem.lower() in found.lower() for found in problems), problems
