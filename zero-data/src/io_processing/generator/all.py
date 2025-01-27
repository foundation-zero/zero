from pathlib import Path

from io_processing.generator.amcs_field_map import AMCSFieldMapCTEGenerator
from io_processing.generator.io_metadata import IOMetadataWriter
from io_processing.marpower import read_amcs_excel, normalize_amcs_io_list, excel_df_to_io_values


def generate():
    repo_root = Path(__file__).parent / "../../.."
    dbt_path = repo_root / "dbt"
    amcs_df = read_amcs_excel(repo_root / "io_lists/52422003_3210_AMCS IO-List R1.11.xlsx")
    normalized_df = normalize_amcs_io_list(amcs_df)
    io_values = excel_df_to_io_values(normalized_df)

    IOMetadataWriter(dbt_path, normalized_df).write_io_metadata_csv()
    AMCSFieldMapCTEGenerator(io_values, dbt_path).generate()
