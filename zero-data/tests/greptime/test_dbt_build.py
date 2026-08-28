"""Top seam: (snapshot-seeded local Greptime) -> `dbt build` green.

Loads the committed snapshot, runs `dbt build`, and asserts the source tests, the proof
view, the model test, and the view's cross-database queryability all pass. No mocking;
local Greptime is assumed running (as in CI and docker-compose).
"""

import json
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
        ["uv", "run", "--project", "..", "dbt", "build", "--log-format", "json"],
        cwd=DBT_DIR,
        env=env,
        capture_output=True,
        text=True,
    )


def _dbt_events(output: str) -> dict[str, list[str]]:
    """Map dbt JSON-log event name -> list of its message strings.

    `--log-format json` emits one {info: {name, msg}} object per line; keying on the
    event name keeps the assertions tied to a dbt log event rather than an ambiguous
    substring in the rendered human output.
    """
    events: dict[str, list[str]] = {}
    for line in output.splitlines():
        try:
            info = json.loads(line)["info"]
        except (json.JSONDecodeError, KeyError):
            continue
        events.setdefault(info.get("name", ""), []).append(info.get("msg", ""))
    return events


def test_dbt_build_is_green_against_snapshot_seeded_greptime(
    connection: GreptimeConnection,
) -> None:
    load_snapshot(connection, SNAPSHOT_DIR)

    result = _dbt_build()

    assert result.returncode == 0, (
        f"dbt build failed:\n{result.stdout}\n{result.stderr}"
    )
    events = _dbt_events(result.stdout)
    # the run summary reports zero errors
    assert any("ERROR=0" in msg for msg in events.get("StatsLine", []))
    assert any(
        "Completed successfully" in msg for msg in events.get("EndOfRunSummary", [])
    )
    # each success is asserted by dbt log event type, not a text substring
    assert any(
        "source_not_null_raw_marpower__150000_propulsion__pcs_fwd_timestamp" in msg
        and "PASS" in msg
        for msg in events.get("LogTestResult", [])
    )
    assert any(
        f"views.{PROOF_VIEW}" in msg and "created" in msg
        for msg in events.get("LogModelResult", [])
    )
    assert any(
        f"not_null_{PROOF_VIEW}_ts" in msg and "PASS" in msg
        for msg in events.get("LogTestResult", [])
    )


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
