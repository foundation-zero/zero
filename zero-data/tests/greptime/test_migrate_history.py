"""migrate-history against a real local Greptime, on synthetic tables.

The old table holds a sounder that was renamed on day 2 (an earlier name of the same device),
and a catch-all topic whose keys belong to two devices in two new tables.
"""

from collections.abc import Iterator
from datetime import date
from pathlib import Path

import psycopg
import pytest

from tests.greptime.conftest import Greptime as Query
from tests.greptime.rehearsal_tables import create_new_tables
from zero_data.greptime import migrate_history
from zero_data.greptime.cli import MigrateCheckCmd, MigrateDropCmd, MigrateRunCmd
from zero_data.greptime.config import GreptimeConnection
from zero_data.greptime.migrate_history import (
    LOCK_TABLE,
    Greptime,
    MigrationFailed,
    check,
    drop,
    leftover,
    load,
    lock,
    report,
    run,
)
from zero_data.greptime.migration_spec import (
    ColumnMap,
    MappingRow,
    MigrationSpec,
    SpecRefused,
    Unit,
    VectorEvent,
    build_spec,
    read_mapping,
)
from zero_data.greptime.snapshot import connect

OLD = "zz_mh_old_fire"
OLD_GENERAL = "zz_mh_old_fire_general"
SOUNDER = "zz_mh_fire__sounder"
GENERAL = "zz_mh_fire__general"
PANEL = "zz_mh_fire__main_panel"
TABLES = (OLD, OLD_GENERAL, SOUNDER, GENERAL, PANEL, LOCK_TABLE)
EARLIER_NAME = "marpower/old-fire/201h1/s"
OLD_SOUNDER = "marpower/old-fire/201h1-s"
NEW_SOUNDER = "marpower/21-fire/sounder/201h1-s"
OLD_CATCH_ALL = "marpower/old-fire-general"

SOUNDER_COLUMNS = [
    ColumnMap(old="alarm", new="alarm"),
    ColumnMap(old="prealarm", new="pre_alarm"),
    ColumnMap(old="level", new="level"),
]
SPEC = MigrationSpec(
    units=[
        Unit(
            old_table=OLD,
            old_topic=EARLIER_NAME,
            new_table=SOUNDER,
            new_topic=NEW_SOUNDER,
            technical_name="201h1-s",
            columns=SOUNDER_COLUMNS,
        ),
        Unit(
            old_table=OLD,
            old_topic=OLD_SOUNDER,
            new_table=SOUNDER,
            new_topic=NEW_SOUNDER,
            technical_name="201h1-s",
            columns=SOUNDER_COLUMNS,
        ),
        Unit(
            old_table=OLD_GENERAL,
            old_topic=OLD_CATCH_ALL,
            new_table=GENERAL,
            new_topic="marpower/21-fire/general",
            technical_name="general",
            columns=[ColumnMap(old="fire_muster", new="muster")],
        ),
        Unit(
            old_table=OLD_GENERAL,
            old_topic=OLD_CATCH_ALL,
            new_table=PANEL,
            new_topic="marpower/21-fire/main-panel",
            technical_name="main-panel",
            columns=[ColumnMap(old="fire_panel_command", new="command")],
        ),
    ]
)


def ts(day: int, hour: int, nanos: int = 0) -> str:
    return f"'2026-08-{day:02d}T{hour:02d}:00:00.{nanos:09d}Z'"


@pytest.fixture
def greptime(connection: GreptimeConnection) -> Iterator[Greptime]:
    with connect(connection.with_dbname("public")) as handle:
        yield Greptime(handle, "public")


@pytest.fixture
def tables(public: Query, greptime: Greptime) -> Iterator[Query]:
    for table in TABLES:
        public.drop_table(table)
    public.execute(
        f'CREATE TABLE "{OLD}" ("timestamp" TIMESTAMP(9) NOT NULL, "topic" STRING NULL, '
        '"alarm__value" BOOLEAN NULL, "alarm__timestamp" STRING NULL, '
        '"prealarm__value" BOOLEAN NULL, "level__value" BIGINT NULL, '
        '"spare__value" BOOLEAN NULL, '
        "TIME INDEX (\"timestamp\")) WITH (append_mode = 'true')"
    )
    public.execute(
        f'CREATE TABLE "{OLD_GENERAL}" ("timestamp" TIMESTAMP(9) NOT NULL, '
        '"topic" STRING NULL, "fire_muster__value" BOOLEAN NULL, '
        '"fire_panel_command__value" BIGINT NULL, '
        "TIME INDEX (\"timestamp\")) WITH (append_mode = 'true')"
    )
    old_rows = [
        (ts(6, 10), EARLIER_NAME, "true", "false", "3", "NULL"),
        (ts(6, 11), EARLIER_NAME, "false", "false", "4", "NULL"),
        (ts(7, 9, 5), EARLIER_NAME, "false", "true", "5", "NULL"),
        # No mapped value: not history of the sounder.
        (ts(7, 9, 7), EARLIER_NAME, "NULL", "NULL", "NULL", "NULL"),
        (ts(7, 10), OLD_SOUNDER, "true", "true", "6", "true"),
        (ts(8, 10), OLD_SOUNDER, "false", "false", "7", "NULL"),
        (ts(8, 11), OLD_SOUNDER, "true", "false", "8", "NULL"),
        (ts(6, 10), "marpower/old-fire/201h2-s", "true", "true", "1", "NULL"),
    ]
    public.execute(
        f'INSERT INTO "{OLD}" ("timestamp", "topic", "alarm__value", "alarm__timestamp", '
        '"prealarm__value", "level__value", "spare__value") VALUES '
        + ", ".join(
            f"({t}, '{topic}', {alarm}, 'stamp', {pre}, {level}, {spare})"
            for t, topic, alarm, pre, level, spare in old_rows
        )
    )
    public.execute(
        f'INSERT INTO "{OLD_GENERAL}" ("timestamp", "topic", "fire_muster__value", '
        '"fire_panel_command__value") VALUES '
        f"({ts(6, 10)}, '{OLD_CATCH_ALL}', true, NULL), "
        f"({ts(6, 11)}, '{OLD_CATCH_ALL}', NULL, 2), "
        f"({ts(8, 11)}, '{OLD_CATCH_ALL}', false, 3)"
    )
    create_new_tables(greptime, SPEC)
    try:
        yield public
    finally:
        for table in TABLES:
            public.drop_table(table)


def no_sleep(_: float) -> None:
    pass


def migrate(greptime: Greptime, until: date | None = None) -> int:
    return run(greptime, load(greptime, SPEC), until, 0, no_sleep)


def sounder_rows(tables: Query) -> list[tuple[object, ...]]:
    return tables.fetch(
        'SELECT "topic", "technical_name", "alarm__value", "alarm__timestamp", '
        f'"pre_alarm__value", "level__value" FROM "{SOUNDER}" ORDER BY "timestamp"'
    )


def test_run_copies_an_earlier_name_and_its_successor_under_the_new_names(
    tables: Query, greptime: Greptime
) -> None:
    assert migrate(greptime) == 10

    assert sounder_rows(tables) == [
        (NEW_SOUNDER, "201h1-s", True, "stamp", False, 3),
        (NEW_SOUNDER, "201h1-s", False, "stamp", False, 4),
        (NEW_SOUNDER, "201h1-s", False, "stamp", True, 5),
        (NEW_SOUNDER, "201h1-s", True, "stamp", True, 6),
        (NEW_SOUNDER, "201h1-s", False, "stamp", False, 7),
        (NEW_SOUNDER, "201h1-s", True, "stamp", False, 8),
    ]
    assert check(greptime, load(greptime, SPEC)) == []


def test_run_splits_a_catch_all_topic_over_its_devices(
    tables: Query, greptime: Greptime
) -> None:
    migrate(greptime)

    assert tables.fetch(
        f'SELECT "topic", "muster__value" FROM "{GENERAL}" ORDER BY "timestamp"'
    ) == [("marpower/21-fire/general", True), ("marpower/21-fire/general", False)]
    assert tables.fetch(
        f'SELECT "technical_name", "command__value" FROM "{PANEL}" ORDER BY "timestamp"'
    ) == [("main-panel", 2), ("main-panel", 3)]


def test_run_copies_a_wide_day_in_parts(
    tables: Query, greptime: Greptime, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(migrate_history, "VALUES_PER_INSERT", 3)
    inserts: list[str] = []

    def recording(sql: str) -> None:
        if sql.startswith("INSERT"):
            inserts.append(sql)
        Greptime.run(greptime, sql)

    monkeypatch.setattr(greptime, "run", recording)

    assert migrate(greptime) == 10

    assert len(inserts) == 14
    assert check(greptime, load(greptime, SPEC)) == []


@pytest.mark.parametrize(
    "dropped",
    [
        psycopg.errors.InternalError_("Internal error: 1003"),
        psycopg.errors.OperatorIntervention("operation was canceled"),
    ],
)
def test_run_sends_a_statement_again_when_greptime_drops_it(
    tables: Query,
    greptime: Greptime,
    monkeypatch: pytest.MonkeyPatch,
    dropped: psycopg.Error,
) -> None:
    failures = [dropped]
    waits: list[float] = []

    def failing_once(sql: str) -> None:
        if sql.startswith("INSERT") and failures:
            raise failures.pop()
        Greptime.run(greptime, sql)

    monkeypatch.setattr(greptime, "run", failing_once)

    assert run(greptime, load(greptime, SPEC), None, 0, waits.append) == 10

    assert migrate_history.RETRY_WAIT in waits
    assert check(greptime, load(greptime, SPEC)) == []


def test_run_counts_a_day_again_when_greptime_drops_the_count(
    tables: Query, greptime: Greptime, monkeypatch: pytest.MonkeyPatch
) -> None:
    failures = [psycopg.errors.InternalError_("Internal error: 1003")]
    waits: list[float] = []

    def failing_once(sql: str) -> int:
        if failures:
            raise failures.pop()
        return Greptime.count(greptime, sql)

    monkeypatch.setattr(greptime, "count", failing_once)

    assert run(greptime, load(greptime, SPEC), None, 0, waits.append) == 10

    assert waits.count(migrate_history.RETRY_WAIT) == 1


def test_run_gives_up_when_greptime_keeps_failing(
    tables: Query, greptime: Greptime, monkeypatch: pytest.MonkeyPatch
) -> None:
    attempts: list[str] = []

    def failing(sql: str) -> None:
        if sql.startswith("INSERT"):
            attempts.append(sql)
            raise psycopg.errors.InternalError_("Internal error: 1003")
        Greptime.run(greptime, sql)

    monkeypatch.setattr(greptime, "run", failing)

    with pytest.raises(psycopg.errors.InternalError_):
        migrate(greptime)

    assert len(attempts) == migrate_history.ATTEMPTS


def test_a_second_run_copies_nothing(tables: Query, greptime: Greptime) -> None:
    migrate(greptime)

    assert migrate(greptime) == 0
    assert len(sounder_rows(tables)) == 6


def test_run_goes_back_no_further_than_until(tables: Query, greptime: Greptime) -> None:
    assert migrate(greptime, until=date(2026, 8, 8)) == 4

    findings = check(greptime, load(greptime, SPEC))
    assert f"{SOUNDER} {NEW_SOUNDER} 2026-08-07: 2 old rows, 0 new rows" in findings
    assert migrate(greptime) == 6
    assert check(greptime, load(greptime, SPEC)) == []


def test_run_completes_a_day_that_was_copied_in_part(
    tables: Query, greptime: Greptime
) -> None:
    load_first = load(greptime, SPEC)
    run(greptime, load_first, date(2026, 8, 9), 0, no_sleep)
    tables.execute(
        f'INSERT INTO "{SOUNDER}" ("timestamp", "topic", "technical_name", '
        f'"alarm__value", "alarm__timestamp", "pre_alarm__value", "level__value") '
        f"VALUES ({ts(8, 10)}, '{NEW_SOUNDER}', '201h1-s', false, 'stamp', false, 7)"
    )

    migrate(greptime)

    assert len(sounder_rows(tables)) == 6
    assert check(greptime, load(greptime, SPEC)) == []


def test_a_column_of_another_type_leaves_its_unit_out_until_it_is_altered(
    tables: Query, greptime: Greptime
) -> None:
    tables.execute(f'ALTER TABLE "{SOUNDER}" ADD COLUMN "level__value" DOUBLE NULL')

    migration = load(greptime, SPEC)

    assert [(m.old_column, m.old_type, m.new_type) for m in migration.mismatches] == [
        ("level__value", "bigint", "double"),
        ("level__value", "bigint", "double"),
    ]
    assert [r.unit.new_table for r in migration.refused] == [SOUNDER, SOUNDER]
    run(greptime, migration, None, 0, no_sleep)
    assert tables.fetch(f'SELECT count(*) FROM "{SOUNDER}"') == [(0,)]
    assert len(check(greptime, load(greptime, SPEC))) == 2

    tables.execute(f'ALTER TABLE "{OLD}" MODIFY COLUMN "level__value" DOUBLE')

    migrate(greptime)
    assert [row[-1] for row in sounder_rows(tables)] == [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    assert check(greptime, load(greptime, SPEC)) == []


def test_two_old_topics_of_one_new_topic_keep_their_rows_at_the_same_moment(
    tables: Query, greptime: Greptime
) -> None:
    tables.execute(
        f'INSERT INTO "{OLD}" ("timestamp", "topic", "spare__value") '
        f"VALUES ({ts(8, 11)}, 'marpower/old-fire/panel', true)"
    )
    spec = MigrationSpec(
        units=[
            *SPEC.units,
            Unit(
                old_table=OLD,
                old_topic="marpower/old-fire/panel",
                new_table=PANEL,
                new_topic="marpower/21-fire/main-panel",
                technical_name="main-panel",
                columns=[ColumnMap(old="spare", new="spare")],
            ),
        ]
    )

    assert run(greptime, load(greptime, spec), None, 0, no_sleep) == 11
    assert run(greptime, load(greptime, spec), None, 0, no_sleep) == 0

    assert tables.fetch(
        f'SELECT "command__value", "spare__value" FROM "{PANEL}" '
        'ORDER BY "timestamp", "command__value"'
    ) == [(2, None), (3, None), (None, True)]
    assert check(greptime, load(greptime, spec)) == []


def foreign_rows(tables: Query, hours: list[int]) -> None:
    tables.execute(
        f'INSERT INTO "{SOUNDER}" ("timestamp", "topic", "technical_name") VALUES '
        + ", ".join(f"({ts(8, hour)}, '{NEW_SOUNDER}', '201h1-s')" for hour in hours)
    )


def test_a_new_topic_with_more_rows_than_the_old_one_is_left_out(
    tables: Query, greptime: Greptime
) -> None:
    foreign_rows(tables, [1, 2, 3])

    migration = load(greptime, SPEC)

    assert {r.unit.new_topic for r in migration.refused} == {NEW_SOUNDER}
    assert "3 against 2 on 2026-08-08" in migration.refused[0].reason
    assert [h.new_table for h in migration.histories] == [GENERAL, PANEL]


def test_run_stops_on_a_day_that_ends_up_with_other_rows_than_the_old_topic(
    tables: Query, greptime: Greptime
) -> None:
    foreign_rows(tables, [1])

    with pytest.raises(MigrationFailed, match="holds 3 rows on 2026-08-08"):
        migrate(greptime)


def test_check_finds_rows_and_values_that_differ(
    tables: Query, greptime: Greptime
) -> None:
    migrate(greptime)
    tables.execute(
        f'INSERT INTO "{OLD}" ("timestamp", "topic", "alarm__value", "level__value") '
        f"VALUES ({ts(8, 12)}, '{OLD_SOUNDER}', true, 99)"
    )

    findings = check(greptime, load(greptime, SPEC))

    assert findings == [
        f"{SOUNDER} {NEW_SOUNDER} 2026-08-08: 3 old rows, 2 new rows",
        f"{SOUNDER} {NEW_SOUNDER} alarm__value: count, min, max (7, False, True) old, "
        "(6, False, True) new",
        f"{SOUNDER} {NEW_SOUNDER} level__value: count, min, max (7, 3, 99) old, "
        "(6, 3, 8) new",
    ]


def test_leftover_names_the_topics_and_columns_no_unit_copies(
    tables: Query, greptime: Greptime
) -> None:
    left = leftover(greptime, SPEC, OLD)

    assert left.topics == {"marpower/old-fire/201h2-s": 1}
    assert left.columns == {OLD_SOUNDER: ["spare__value"]}
    assert not leftover(greptime, SPEC, OLD_GENERAL)


def test_the_report_lists_what_a_run_would_do(
    tables: Query, greptime: Greptime
) -> None:
    text = report(load(greptime, SPEC), {OLD: leftover(greptime, SPEC, OLD)})

    assert "10 rows in 4 units, 0 already copied" in text
    assert f"| `{SOUNDER}` | 4 |" in text
    assert "`marpower/old-fire/201h2-s` | 1 | all" in text
    assert "`spare__value`" in text


def test_drop_keeps_a_table_until_its_history_is_checked(
    tables: Query, greptime: Greptime
) -> None:
    outcomes = drop(greptime, SPEC, [OLD_GENERAL], True, True)

    assert outcomes == {OLD_GENERAL: "kept: 6 check findings"}
    assert OLD_GENERAL in greptime.tables()


def test_drop_removes_checked_tables_and_asks_before_losing_data(
    tables: Query, greptime: Greptime
) -> None:
    migrate(greptime)

    assert drop(greptime, SPEC, [], False, False) == {
        OLD: "kept: not migrated: 1 topics, and columns of 1 migrated topics",
        OLD_GENERAL: "would be dropped",
    }
    assert drop(greptime, SPEC, [], False, True)[OLD_GENERAL] == "dropped"
    assert drop(greptime, SPEC, [OLD], True, True) == {OLD: "dropped"}
    assert greptime.tables().isdisjoint({OLD, OLD_GENERAL})
    assert drop(greptime, SPEC, [], False, True) == {
        OLD: "already gone",
        OLD_GENERAL: "already gone",
    }


def test_drop_checks_old_tables_of_one_new_topic_before_dropping_either(
    tables: Query, greptime: Greptime
) -> None:
    spec = MigrationSpec(
        units=[
            *SPEC.units,
            Unit(
                old_table=OLD,
                old_topic=OLD_SOUNDER,
                new_table=PANEL,
                new_topic="marpower/21-fire/main-panel",
                technical_name="main-panel",
                columns=[ColumnMap(old="spare", new="spare")],
            ),
        ]
    )
    run(greptime, load(greptime, spec), None, 0, no_sleep)

    outcomes = drop(greptime, spec, [OLD, OLD_GENERAL], True, True)

    assert outcomes == {OLD: "dropped", OLD_GENERAL: "dropped"}


def test_drop_keeps_a_table_that_still_receives_rows(
    tables: Query, greptime: Greptime
) -> None:
    migrate(greptime)
    tables.execute(
        f'INSERT INTO "{OLD_GENERAL}" ("timestamp", "topic") VALUES (now(), \'other\')'
    )

    outcome = drop(greptime, SPEC, [OLD_GENERAL], True, True)[OLD_GENERAL]

    assert outcome == "kept: 1 rows in the last day"


def test_a_second_run_is_refused_while_one_holds_the_lock(
    tables: Query, greptime: Greptime
) -> None:
    with lock(greptime):
        with pytest.raises(MigrationFailed, match="A run or drop holds the lock"):
            with lock(greptime):
                pass

    with lock(greptime):
        assert LOCK_TABLE in greptime.tables()
    assert LOCK_TABLE not in greptime.tables()


def test_a_failed_run_releases_the_lock_and_unlock_clears_one_left_behind(
    tables: Query, greptime: Greptime
) -> None:
    foreign_rows(tables, [1])
    with pytest.raises(MigrationFailed, match="holds 3 rows"):
        with lock(greptime):
            migrate(greptime)
    assert LOCK_TABLE not in greptime.tables()

    tables.execute(
        f'CREATE TABLE "{LOCK_TABLE}" ("started" TIMESTAMP(3) TIME INDEX, "host" STRING)'
    )
    with pytest.raises(MigrationFailed, match="--unlock"):
        with lock(greptime):
            pass
    with lock(greptime, unlock=True):
        pass
    assert LOCK_TABLE not in greptime.tables()


def test_drop_is_refused_while_a_run_holds_the_lock(
    tables: Query, greptime: Greptime, tmp_path: Path
) -> None:
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(SPEC.model_dump_json())
    migrate(greptime)

    with lock(greptime):
        with pytest.raises(MigrationFailed, match="A run or drop holds the lock"):
            MigrateDropCmd(spec=spec_path, table=[OLD_GENERAL], execute=True).cli_cmd()
    assert OLD_GENERAL in greptime.tables()


def test_load_refuses_a_table_the_spec_does_not_have(
    tables: Query, greptime: Greptime
) -> None:
    with pytest.raises(MigrationFailed, match="Not an old table"):
        load(greptime, SPEC, ["zz_mh_unknown"])


def test_the_commands_run_check_and_drop(
    tables: Query, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(SPEC.model_dump_json())

    MigrateRunCmd(spec=spec_path, dry_run=True).cli_cmd()
    assert "10 rows in 4 units" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        MigrateCheckCmd(spec=spec_path).cli_cmd()
    MigrateRunCmd(spec=spec_path, pause=0).cli_cmd()
    MigrateCheckCmd(spec=spec_path).cli_cmd()
    MigrateDropCmd(spec=spec_path, table=[OLD_GENERAL]).cli_cmd()
    assert f"{OLD_GENERAL}: would be dropped" in capsys.readouterr().out
    with pytest.raises(SystemExit, match="needs the tables named"):
        MigrateDropCmd(spec=spec_path, accept_unmigrated=True).cli_cmd()


MAPPING = [
    MappingRow(
        old_topic="marpower/old-fire/201h1-s",
        old_key="PreAlarm",
        new_topic="marpower/21-fire/sounder/201h1-s",
        new_key="Pre_Alarm",
    ),
    MappingRow(
        old_topic="marpower/old-fire/201h1-s",
        old_key="Alarm",
        new_topic="marpower/21-fire/sounder/201h1-s",
        new_key="Alarm",
    ),
]


def fake_vector(cases: list[dict[str, str]]) -> list[VectorEvent]:
    import json

    events: list[VectorEvent] = []
    for case in cases:
        message = json.loads(case["message"])
        key = next(k for k in message if k != "ZzCase")
        old = case["topic"].startswith("marpower/old-fire")
        events.append(
            {
                "zz_case": message["ZzCase"],
                "topic": case["topic"],
                "table": "old_fire" if old else "fire__sounder",
                **({} if old else {"technical_name": case["topic"].rsplit("/", 1)[1]}),
                f"{key.lower()}__value": 1.5,
            }
        )
    return events


def test_build_spec_takes_table_and_column_names_from_vector() -> None:
    spec = build_spec(MAPPING, fake_vector)

    assert spec.units == [
        Unit(
            old_table="old_fire",
            old_topic="marpower/old-fire/201h1-s",
            new_table="fire__sounder",
            new_topic="marpower/21-fire/sounder/201h1-s",
            technical_name="201h1-s",
            columns=[
                ColumnMap(old="alarm", new="alarm"),
                ColumnMap(old="prealarm", new="pre_alarm"),
            ],
        )
    ]


def test_build_spec_refuses_a_message_vector_drops() -> None:
    with pytest.raises(SpecRefused, match="Vector dropped 2 messages"):
        build_spec(MAPPING, lambda cases: fake_vector(cases[:2]))


def test_read_mapping_wants_the_four_columns(tmp_path: Path) -> None:
    mapping_path = tmp_path / "mapping.csv"
    mapping_path.write_text("old_topic,old_key,new_topic,new_key\na,B,c,D\n")
    assert read_mapping(mapping_path) == [
        MappingRow(old_topic="a", old_key="B", new_topic="c", new_key="D")
    ]

    mapping_path.write_text("topic,key\na,B\n")
    with pytest.raises(SpecRefused, match="must have the columns"):
        read_mapping(mapping_path)
