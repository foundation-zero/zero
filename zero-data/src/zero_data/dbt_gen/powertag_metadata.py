import logging
from pathlib import Path
import gspread
import polars as pl

SERVICE_ACCOUNT_KEY_FILE = ".gsheet-sa-key.json"  # Stored in Bitwarden IT / Zero / Common GSheet Service Account
SHEET_ID = "1aPp87gaevQulzXpWf-wpg5ScPD3WNuJPkMSB4weMQd8"

logger = logging.getLogger(__name__)


class PowerTagMetadataGenerator:
    def __init__(self, dbt_path: Path):
        self.seed_path = dbt_path / "seeds/"

    def generate(self):
        # Write the metadata to a Google Sheet
        metadata_path = (self.seed_path / "power_tag_metadata.csv").resolve()
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_KEY_FILE)
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet("Powertags")
        data = worksheet.get_all_records()
        df = pl.DataFrame(data)
        df = df.rename(lambda col_name: col_name.lower().replace(" ", "_"))
        df.write_csv(metadata_path, quote_style="non_numeric")
        logger.info(
            f"Wrote {df.shape[0]} rows and {df.shape[1]} columns to {metadata_path}"
        )
