"""migrate-history against a real local Greptime: plan, execute and check on synthetic tables.

The old table holds a sounder that was renamed on day 2 (a chain), and a catch-all topic whose
keys belong to two devices in two new tables.
"""

import fcntl
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from tests.greptime.conftest import Greptime as Query
from zero_data.greptime.cli import MigratePlanCmd
from zero_data.greptime.config import GreptimeConnection
from zero_data.greptime.migrate_history import (
    Greptime,
    MigrationRefused,
    Window,
    _Draft,
    _overlapping,
    check_plan,
    execute_plan,
    plan_migration,
    to_nanos,
    wave_paths,
)
from zero_data.greptime.migration_spec import ColumnMap, MigrationSpec, Unit
from zero_data.greptime.snapshot import connect

OLD = "zz_mh_old_fire"
OLD_GENERAL = "zz_mh_old_fire_general"
SOUNDER = "zz_mh_fire__sounder"
GENERAL = "zz_mh_fire__general"
PANEL = "zz_mh_fire__main_panel"
TABLES = (OLD, OLD_GENERAL, SOUNDER, GENERAL, PANEL)
BOUNDARY = datetime(2026, 8, 10, tzinfo=UTC)
ENDPOINT = "127.0.0.1:4003/public"


def column(old: str, new: str) -> ColumnMap:
    return ColumnMap(old=old, new=new, suffixes=["value", "timestamp"])


SOUNDER_COLUMNS = [
    column("alarm", "alarm"),
    column("prealarm", "pre_alarm"),
    column("level", "level"),
    column("test", "test"),
]
SPEC = MigrationSpec(
    units=[
        Unit(
            wave=1,
            old_table=OLD,
            old_topic="marpower/old-fire/201h1/s",
            new_table=SOUNDER,
            new_topic="marpower/21-fire/sounder/201h1-s",
            technical_name="201h1-s",
            columns=SOUNDER_COLUMNS,
            chain="earlier name",
        ),
        Unit(
            wave=1,
            old_table=OLD,
            old_topic="marpower/old-fire/201h1-s",
            new_table=SOUNDER,
            new_topic="marpower/21-fire/sounder/201h1-s",
            technical_name="201h1-s",
            columns=SOUNDER_COLUMNS,
        ),
        Unit(
            wave=2,
            old_table=OLD_GENERAL,
            old_topic="marpower/old-fire-general",
            new_table=GENERAL,
            new_topic="marpower/21-fire/general",
            technical_name="general",
            columns=[column("fire_muster", "muster")],
        ),
        Unit(
            wave=2,
            old_table=OLD_GENERAL,
            old_topic="marpower/old-fire-general",
            new_table=PANEL,
            new_topic="marpower/21-fire/main-panel",
            technical_name="main-panel",
            columns=[column("fire_panel_command", "command")],
        ),
    ]
)


def ts(day: int, hour: int, nanos: int = 0) -> str:
    return f"'2026-08-{day:02d}T{hour:02d}:00:00.{nanos:09d}Z'"


@pytest.fixture
def tables(public: Query) -> Iterator[Query]:
    for table in TABLES:
        public.drop_table(table)
    public.execute(
        f'CREATE TABLE "{OLD}" ("timestamp" TIMESTAMP(9) NOT NULL, "topic" STRING NULL, '
        '"source_type" STRING NULL, "table" STRING NULL, '
        '"alarm__value" BOOLEAN NULL, "alarm__timestamp" STRING NULL, '
        '"prealarm__value" BOOLEAN NULL, "prealarm__timestamp" STRING NULL, '
        '"level__value" BIGINT NULL, "level__timestamp" STRING NULL, '
        '"test__value" BOOLEAN NULL, "test__timestamp" STRING NULL, '
        '"spare__value" BOOLEAN NULL, '
        "TIME INDEX (\"timestamp\")) WITH (append_mode = 'true')"
    )
    public.execute(
        f'CREATE TABLE "{OLD_GENERAL}" ("timestamp" TIMESTAMP(9) NOT NULL, "topic" STRING NULL, '
        '"fire_muster__value" BOOLEAN NULL, "fire_muster__timestamp" STRING NULL, '
        '"fire_panel_command__value" BIGINT NULL, "fire_panel_command__timestamp" STRING NULL, '
        "TIME INDEX (\"timestamp\")) WITH (append_mode = 'true')"
    )
    public.execute(
        f'CREATE TABLE "{SOUNDER}" ("timestamp" TIMESTAMP(9) NOT NULL, "topic" STRING NULL, '
        '"technical_name" STRING NULL, "alarm__value" BOOLEAN NULL, '
        '"alarm__timestamp" STRING NULL, "pre_alarm__value" BOOLEAN NULL, '
        '"pre_alarm__timestamp" STRING NULL, "level__value" DOUBLE NULL, '
        '"level__timestamp" STRING NULL, "spare__value" BOOLEAN NULL, '
        "TIME INDEX (\"timestamp\")) WITH (append_mode = 'true')"
    )
    for table, column_name in ((GENERAL, "muster"), (PANEL, "command")):
        value_type = "BOOLEAN" if column_name == "muster" else "BIGINT"
        public.execute(
            f'CREATE TABLE "{table}" ("timestamp" TIMESTAMP(9) NOT NULL, "topic" STRING NULL, '
            f'"technical_name" STRING NULL, "{column_name}__value" {value_type} NULL, '
            f'"{column_name}__timestamp" STRING NULL, '
            "TIME INDEX (\"timestamp\")) WITH (append_mode = 'true')"
        )
    old_rows = [
        # The chain: 6 Aug and 7 Aug until 09h, then renamed.
        (ts(6, 10), "marpower/old-fire/201h1/s", "true", "false", "3", "true", "true"),
        (ts(6, 11), "marpower/old-fire/201h1/s", "false", "false", "4", "NULL", "NULL"),
        (
            ts(7, 9, 5),
            "marpower/old-fire/201h1/s",
            "false",
            "true",
            "5",
            "false",
            "NULL",
        ),
        # A row without any mapped value: not copied.
        (
            ts(7, 9, 7),
            "marpower/old-fire/201h1/s",
            "NULL",
            "NULL",
            "NULL",
            "NULL",
            "NULL",
        ),
        (ts(7, 10), "marpower/old-fire/201h1-s", "true", "true", "6", "false", "false"),
        (ts(8, 10), "marpower/old-fire/201h1-s", "false", "false", "7", "NULL", "NULL"),
        # After the new topic's first row (9 Aug 12h): left alone.
        (ts(9, 13), "marpower/old-fire/201h1-s", "true", "true", "8", "NULL", "NULL"),
        # Another sounder, not in the spec.
        (ts(6, 10), "marpower/old-fire/201h2-s", "true", "true", "1", "NULL", "NULL"),
    ]
    public.execute(
        f'INSERT INTO "{OLD}" ("timestamp", "topic", "source_type", "table", "alarm__value", '
        '"alarm__timestamp", "prealarm__value", "level__value", "test__value", "spare__value") '
        "VALUES "
        + ", ".join(
            f"({t}, '{topic}', 'mqtt', '{OLD}', {alarm}, 'stamp', {pre}, {level}, {test}, {spare})"
            for t, topic, alarm, pre, level, test, spare in old_rows
        )
    )
    public.execute(
        f'INSERT INTO "{OLD_GENERAL}" ("timestamp", "topic", "fire_muster__value", '
        '"fire_panel_command__value") VALUES '
        f"({ts(6, 10)}, 'marpower/old-fire-general', true, NULL), "
        f"({ts(6, 11)}, 'marpower/old-fire-general', NULL, 2), "
        f"({ts(8, 11)}, 'marpower/old-fire-general', false, 3)"
    )
    public.execute(
        f'INSERT INTO "{SOUNDER}" ("timestamp", "topic", "technical_name", "alarm__value") '
        f"VALUES ({ts(9, 12)}, 'marpower/21-fire/sounder/201h1-s', '201h1-s', true)"
    )
    try:
        yield public
    finally:
        for table in TABLES:
            public.drop_table(table)


@pytest.fixture
def greptime(connection: GreptimeConnection) -> Iterator[Greptime]:
    with connect(connection.with_dbname("public")) as handle:
        yield Greptime(handle, "public")


def plan(greptime: Greptime, out: Path, spec: MigrationSpec = SPEC) -> list[Path]:
    return plan_migration(
        greptime, spec, "spec-sha", ENDPOINT, to_nanos(BOUNDARY), [], out
    )


def no_sleep(_: float) -> None:
    pass


def test_execute_copies_the_chain_and_its_successor_under_the_new_names(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    plan(greptime, tmp_path)

    statuses = execute_plan(greptime, tmp_path / "wave-1.sql", ENDPOINT, 0, no_sleep)

    assert statuses == {"added": 2, "copied": 4}
    rows = tables.fetch(
        'SELECT "timestamp", "topic", "technical_name", "alarm__value", "pre_alarm__value", '
        f'"level__value", "test__value", "test__timestamp", "spare__value" FROM "{SOUNDER}" '
        'ORDER BY "timestamp"'
    )
    topic = "marpower/21-fire/sounder/201h1-s"
    assert [row[1:] for row in rows] == [
        (topic, "201h1-s", True, False, 3.0, True, None, True),
        (topic, "201h1-s", False, False, 4.0, None, None, None),
        (topic, "201h1-s", False, True, 5.0, False, None, None),
        (topic, "201h1-s", True, True, 6.0, False, None, False),
        (topic, "201h1-s", False, False, 7.0, None, None, None),
        (topic, "201h1-s", True, None, None, None, None, None),
    ]
    assert tables.columns(SOUNDER, schema="public")[-2:] == [
        ("test__timestamp", "string"),
        ("test__value", "boolean"),
    ]
    assert check_plan(greptime, tmp_path / "wave-1.sql", ENDPOINT)


def test_a_catch_all_topic_splits_into_one_topic_per_device(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    plan(greptime, tmp_path)

    execute_plan(greptime, tmp_path / "wave-2.sql", ENDPOINT, 0, no_sleep)

    assert tables.fetch(
        f'SELECT "topic", "technical_name", "muster__value" FROM "{GENERAL}" ORDER BY "timestamp"'
    ) == [
        ("marpower/21-fire/general", "general", True),
        ("marpower/21-fire/general", "general", False),
    ]
    assert tables.fetch(
        f'SELECT "topic", "technical_name", "command__value" FROM "{PANEL}" ORDER BY "timestamp"'
    ) == [
        ("marpower/21-fire/main-panel", "main-panel", 2),
        ("marpower/21-fire/main-panel", "main-panel", 3),
    ]
    assert check_plan(greptime, tmp_path / "wave-2.sql", ENDPOINT)


def test_the_plan_names_its_bounds_columns_and_live_keys(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    plan(greptime, tmp_path)

    manifest = json.loads((tmp_path / "wave-1.plan.json").read_text())
    assert manifest["added_columns"] == {
        SOUNDER: {"test__timestamp": "string", "test__value": "boolean"}
    }
    chain, successor = manifest["units"]
    assert chain["bound_from"] == successor["bound_from"] == "first row"
    assert [(w["rows"]) for w in chain["windows"]] == [2, 1]
    assert [(w["rows"]) for w in successor["windows"]] == [1, 1]
    assert chain["windows"][-1]["end"] <= successor["windows"][0]["start"]
    assert successor["live_keys"] == ["spare"]
    assert {(c["old"], c["new"], c["cast"]) for c in chain["copies"]} >= {
        ("prealarm__value", "pre_alarm__value", False),
        ("level__value", "level__value", True),
    }
    sql = (tmp_path / "wave-1.sql").read_text()
    assert 'CAST("level__value" AS DOUBLE)' in sql
    assert '"source_type"' not in sql


def test_a_second_execute_copies_nothing(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    plan(greptime, tmp_path)
    sql_path = tmp_path / "wave-1.sql"
    execute_plan(greptime, sql_path, ENDPOINT, 0, no_sleep)

    assert execute_plan(greptime, sql_path, ENDPOINT, 0, no_sleep) == {"journalled": 6}

    _, journal, _ = wave_paths(sql_path)
    journal.write_text(
        "".join(
            line + "\n"
            for line in journal.read_text().splitlines()
            if '"added"' in line
        )
    )
    assert execute_plan(greptime, sql_path, ENDPOINT, 0, no_sleep) == {
        "journalled": 2,
        "present": 4,
    }
    assert tables.fetch(f'SELECT count(*) FROM "{SOUNDER}"') == [(6,)]


def test_a_window_holding_part_of_its_rows_gets_the_rest(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    plan(greptime, tmp_path)
    tables.execute(
        f'INSERT INTO "{SOUNDER}" ("timestamp", "topic", "alarm__value") '
        f"VALUES ({ts(6, 10)}, 'marpower/21-fire/sounder/201h1-s', true)"
    )

    statuses = execute_plan(greptime, tmp_path / "wave-1.sql", ENDPOINT, 0, no_sleep)

    assert statuses["copied"] == 4
    assert tables.fetch(
        f'SELECT "timestamp", "alarm__value" FROM "{SOUNDER}" '
        f'WHERE "timestamp" < {ts(7, 0)} ORDER BY 1'
    ) == [
        (datetime(2026, 8, 6, 10), True),
        (datetime(2026, 8, 6, 11), False),
    ]


def test_a_window_that_ends_up_with_other_than_its_rows_stops_the_run_again(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    plan(greptime, tmp_path)
    sql_path = tmp_path / "wave-1.sql"
    tables.execute(
        f'INSERT INTO "{SOUNDER}" ("timestamp", "topic") '
        f"VALUES ({ts(6, 12)}, 'marpower/21-fire/sounder/201h1-s')"
    )

    with pytest.raises(MigrationRefused, match="holds 3 of 2 rows"):
        execute_plan(greptime, sql_path, ENDPOINT, 0, no_sleep)
    with pytest.raises(MigrationRefused, match="holds 3 of 2 rows"):
        execute_plan(greptime, sql_path, ENDPOINT, 0, no_sleep)


def test_execute_refuses_a_changed_sql_file_or_another_host(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    plan(greptime, tmp_path)
    sql_path = tmp_path / "wave-1.sql"

    with pytest.raises(MigrationRefused, match="planned for 127.0.0.1:4003/public"):
        execute_plan(greptime, sql_path, "127.0.0.1:4003/other", 0, no_sleep)

    sql_path.write_text(sql_path.read_text().replace("2026-08-06", "2026-08-05"))
    with pytest.raises(MigrationRefused, match="sha256 differs"):
        execute_plan(greptime, sql_path, ENDPOINT, 0, no_sleep)


def test_execute_refuses_a_column_that_appeared_since_the_plan(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    plan(greptime, tmp_path)
    tables.execute(f'ALTER TABLE "{SOUNDER}" ADD COLUMN "test__value" BOOLEAN NULL')

    with pytest.raises(
        MigrationRefused, match="test__value has appeared since the plan"
    ):
        execute_plan(greptime, tmp_path / "wave-1.sql", ENDPOINT, 0, no_sleep)


def test_a_plan_built_twice_is_byte_identical(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    first = plan(greptime, tmp_path / "first")
    second = plan(greptime, tmp_path / "second")

    assert [p.name for p in first] == [p.name for p in second]
    assert all(
        a.read_bytes() == b.read_bytes() for a, b in zip(first, second, strict=True)
    )


def test_plan_casts_without_loss_and_refuses_a_table_with_foreign_rows(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    tables.drop_table(GENERAL)
    tables.execute(
        f'CREATE TABLE "{GENERAL}" ("timestamp" TIMESTAMP(9) NOT NULL, "topic" STRING NULL, '
        '"muster__value" STRING NULL, '
        "TIME INDEX (\"timestamp\")) WITH (append_mode = 'true')"
    )
    tables.execute(
        f'INSERT INTO "{PANEL}" ("timestamp", "topic") '
        f"VALUES ({ts(1, 0)}, 'marpower/someone-else')"
    )

    plan(greptime, tmp_path)

    manifest = json.loads((tmp_path / "wave-2.plan.json").read_text())
    reasons = {r["new_table"]: r["reason"] for r in manifest["refused"]}
    assert reasons[PANEL].startswith("The new table holds rows before the boundary")
    assert manifest["units"][0]["new_table"] == GENERAL
    assert manifest["units"][0]["copies"][0]["cast"] is True


def test_plan_refuses_a_cast_from_text_to_a_number(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    tables.drop_table(PANEL)
    tables.execute(
        f'CREATE TABLE "{PANEL}" ("timestamp" TIMESTAMP(9) NOT NULL, "topic" STRING NULL, '
        '"command__value" BOOLEAN NULL, '
        "TIME INDEX (\"timestamp\")) WITH (append_mode = 'true')"
    )

    plan(greptime, tmp_path)

    manifest = json.loads((tmp_path / "wave-2.plan.json").read_text())
    assert [r["reason"] for r in manifest["refused"]] == [
        "fire_panel_command__value is bigint and command__value is boolean: "
        "a cast would lose values"
    ]


def test_plan_refuses_old_topics_whose_periods_overlap_on_one_new_topic(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    tables.execute(
        f'INSERT INTO "{OLD}" ("timestamp", "topic", "alarm__value") '
        f"VALUES ({ts(8, 0)}, 'marpower/old-fire/201h1/s', true)"
    )

    plan(greptime, tmp_path)

    manifest = json.loads((tmp_path / "wave-1.plan.json").read_text())
    assert manifest["units"] == []
    assert len(manifest["refused"]) == 2
    assert all("overlaps" in r["reason"] for r in manifest["refused"])


def draft(old_topic: str, start: int, end: int) -> _Draft:
    unit = SPEC.units[0].model_copy(update={"old_topic": old_topic})
    return _Draft(
        unit=unit,
        pairs=[],
        filter_columns=[],
        live_keys=[],
        absent_old_columns=[],
        bound=100,
        bound_from="first row",
        old_rows=0,
        windows=[Window(start=start, end=end, rows=1)],
    )


def test_a_period_inside_a_long_one_overlaps_it_even_after_a_gap() -> None:
    drafts = [draft("long", 0, 50), draft("early", 10, 20), draft("late", 30, 40)]

    assert sorted(_overlapping(drafts)) == [0, 1, 2]


def test_execute_refuses_while_another_execute_holds_the_journal(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    plan(greptime, tmp_path)
    sql_path = tmp_path / "wave-1.sql"
    _, journal_path, _ = wave_paths(sql_path)

    with journal_path.open("a") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        with pytest.raises(MigrationRefused, match="Another execute"):
            execute_plan(greptime, sql_path, ENDPOINT, 0, no_sleep)


def test_check_reports_the_units_the_plan_refused(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    tables.execute(
        f'INSERT INTO "{PANEL}" ("timestamp", "topic") '
        f"VALUES ({ts(1, 0)}, 'marpower/someone-else')"
    )
    plan(greptime, tmp_path)
    sql_path = tmp_path / "wave-2.sql"
    execute_plan(greptime, sql_path, ENDPOINT, 0, no_sleep)

    check_plan(greptime, sql_path, ENDPOINT)

    _, _, report_path = wave_paths(sql_path)
    assert "1 units were refused by the plan and not copied" in report_path.read_text()


def test_plan_refuses_a_boundary_without_a_timezone() -> None:
    with pytest.raises(ValidationError, match="timezone"):
        MigratePlanCmd.model_validate(
            {"spec": "spec.json", "boundary": "2026-11-17T10:00:00", "out": "out"}
        )


def test_plan_copies_only_the_suffixes_the_spec_lists(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    value_only = ColumnMap(old="fire_muster", new="muster", suffixes=["value"])
    spec = MigrationSpec(
        units=[SPEC.units[2].model_copy(update={"columns": [value_only]})]
    )

    plan(greptime, tmp_path, spec)

    manifest = json.loads((tmp_path / "wave-2.plan.json").read_text())
    assert [c["new"] for c in manifest["units"][0]["copies"]] == ["muster__value"]


def test_plan_refuses_a_unit_whose_new_table_does_not_exist_yet(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    tables.drop_table(PANEL)

    plan(greptime, tmp_path)

    manifest = json.loads((tmp_path / "wave-2.plan.json").read_text())
    assert [(r["new_table"], r["reason"]) for r in manifest["refused"]] == [
        (PANEL, "The new table doesn't exist yet")
    ]
    assert [u["new_table"] for u in manifest["units"]] == [GENERAL]
