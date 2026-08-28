"""Seam 2 (the top seam): `(local Greptime loaded with the snapshot DDL) -> dbt build green`.

Loads the committed snapshot into a real local Greptime, runs `dbt build`, and asserts the
source tests, the proof view, and the model test all pass — then that the view is queryable
with its explicit columns across the `views` -> `public` database boundary. This is the
highest-value seam: it exercises the view SQL, the explicit-column contract, the
Greptime-specific macro overrides, and cross-database resolution end to end.

No database mocking; the local Greptime is assumed running (as in CI and docker-compose).
"""

import os
import subprocess

from tests.greptime.conftest import Greptime
from zero_data.greptime.config import PROJECT_ROOT, SNAPSHOT_DIR, GreptimeConnection
from zero_data.greptime.snapshot import load_snapshot

DBT_DIR = PROJECT_ROOT / "dbt"
PROOF_VIEW = "stg_marpower__150000_propulsion__pcs_fwd"


def _dbt_build() -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "DBT_PROFILES_DIR": str(DBT_DIR)}
    return subprocess.run(
        ["uv", "run", "--project", "..", "dbt", "build"],
        cwd=DBT_DIR,
        env=env,
        capture_output=True,
        text=True,
    )


def test_dbt_build_is_green_against_snapshot_seeded_greptime(
    connection: GreptimeConnection,
) -> None:
    load_snapshot(connection, SNAPSHOT_DIR)

    result = _dbt_build()

    assert result.returncode == 0, (
        f"dbt build failed:\n{result.stdout}\n{result.stderr}"
    )
    output = result.stdout
    assert "Completed successfully" in output
    assert "ERROR=0" in output  # the run summary reports zero errors
    # the source test, the view model, and the model test each report success
    assert (
        "source_not_null_raw_marpower__150000_propulsion__pcs_fwd_timestamp" in output
    )
    assert f"view model views.{PROOF_VIEW}" in output
    assert f"not_null_{PROOF_VIEW}_ts" in output


def test_proof_view_is_queryable_with_explicit_columns(
    connection: GreptimeConnection,
) -> None:
    """The view materializes into `views` and resolves across the database boundary."""
    load_snapshot(connection, SNAPSHOT_DIR)
    assert _dbt_build().returncode == 0

    explicit_columns = [
        "ts",
        "device_state",
        "drive_thermal_state",
        "command_register",
        "azimuth_setpoint_not_reached",
    ]
    views = Greptime(connection, "views")
    # Selecting the exact explicit columns proves the contract and cross-db resolution.
    rows = views.fetch(
        f"select {', '.join(explicit_columns)} from {PROOF_VIEW} limit 1"
    )
    assert rows == []  # snapshot tables are empty; the query resolving is the assertion

    view_columns = views.column_names(f"select * from {PROOF_VIEW} limit 0")
    assert view_columns == explicit_columns
