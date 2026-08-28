from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo layout: <project>/src/zero_greptime_data/config.py -> <project>.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Committed DDL snapshot of the curated raw tables, and the curated table list that drives it.
SNAPSHOT_DIR = PROJECT_ROOT / "snapshot"
CURATED_TABLES_FILE = SNAPSHOT_DIR / "tables.txt"

# Databases dbt needs beyond the raw `public`: the `greptime`-named landing database the dbt
# connection points at (see docs/viability-check.md) and the `views` materialization target.
DBT_DATABASES = ("greptime", "views")


class GreptimeConnection(BaseSettings):
    """Connection to a Greptime instance over its Postgres wire endpoint.

    Fields map to `GREPTIME_*` env vars, matching the `env_var(...)` defaults in
    `dbt/profiles.yml`, so the same environment configures both the tooling and dbt.
    """

    model_config = SettingsConfigDict(env_prefix="GREPTIME_")

    host: str = "127.0.0.1"
    pg_port: int = 4003
    user: str = "app"
    password: str = ""
    # The database to connect to for raw-table operations. `public` is where Vector ingests.
    dbname: str = "public"

    def with_dbname(self, dbname: str) -> "GreptimeConnection":
        return self.model_copy(update={"dbname": dbname})


def read_curated_tables(tables_file: Path = CURATED_TABLES_FILE) -> list[str]:
    """The curated list of raw tables to snapshot — one table name per line.

    Kept deliberately small so snapshot diffs stay focused on tables we actually model.
    """
    lines = tables_file.read_text().splitlines()
    return [
        stripped
        for line in lines
        if (stripped := line.strip()) and not stripped.startswith("#")
    ]
