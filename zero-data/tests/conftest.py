from pathlib import Path

import pytest

from io_processing.marpower import read_amcs_excel, normalize_amcs_io_list, excel_df_to_io_values


@pytest.fixture
def marpower_normalized_df():
    repo_root = Path(__file__).parent / ".."
    amcs_df = read_amcs_excel(repo_root / "io_lists/52422003_3210_AMCS IO-List R1.11.xlsx")
    return normalize_amcs_io_list(amcs_df)

@pytest.fixture
def marpower_io_values(marpower_normalized_df):
    return excel_df_to_io_values(marpower_normalized_df)