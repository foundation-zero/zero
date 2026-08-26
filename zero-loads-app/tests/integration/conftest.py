from uuid import uuid4

import pytest
from aiomqtt import Client as MqttClient
from asgi_lifespan import LifespanManager
from factory.base import DictFactory
from factory.declarations import LazyFunction, Sequence
from httpx import ASGITransport, AsyncClient
from psycopg import connect
from pytest import fixture
from pytest_postgresql import factories
from sqlalchemy import bindparam, select, text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT

import loads.api.dependencies as api_dependencies
from loads.api.api import app
from loads.api.db import SessionManager
from loads.api.schema import (
    AwsRanges,
    LoadCaseMappings,
    LoadCases,
    ReferenceValues,
    SailSetsCombined,
)
from loads.config import Settings

_INTEGRATION_SETTINGS = Settings()  # type: ignore[call-arg]


def clear_mutating_tables(
    host: str,
    port: int,
    user: str,
    dbname: str,
    password: str | None,
):
    with connect(
        host=host,
        port=port,
        user=user,
        dbname=dbname,
        password=password,
        autocommit=True,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM loads.reference_values")
            cursor.execute("DELETE FROM loads.load_case_mappings")
            cursor.execute("DELETE FROM loads.load_cases")


class ExistingDatabaseRef:
    def __init__(self, host: str, port: str, user: str, password: str, dbname: str):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.options = ""
        self._template_dbname = dbname

    @property
    def template_dbname(self) -> str:
        return self._template_dbname


integration_admin_noproc = factories.postgresql_noproc(
    host=_INTEGRATION_SETTINGS.pg_host,
    port=_INTEGRATION_SETTINGS.pg_port,
    user=_INTEGRATION_SETTINGS.pg_user,
    password=_INTEGRATION_SETTINGS.pg_password,
    dbname="pytest_admin",
)
integration_test_source_noproc = factories.postgresql_noproc(
    depends_on="zero_db",
    dbname="zero_it_source",
    load=[clear_mutating_tables],
)
integration_postgresql = factories.postgresql(
    "integration_test_source_noproc", dbname="zero_it_client"
)


@fixture(scope="session")
def zero_db(integration_admin_noproc):
    return ExistingDatabaseRef(
        host=integration_admin_noproc.host,
        port=str(integration_admin_noproc.port),
        user=integration_admin_noproc.user,
        password=integration_admin_noproc.password or "",
        dbname=_INTEGRATION_SETTINGS.pg_db,
    )


@fixture
def integration_db_name(integration_postgresql):
    return integration_postgresql.info.dbname


@fixture(autouse=True)
def configure_integration_db(integration_db_name: str):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("PG_DB", integration_db_name)

    # Rehydrate runtime settings/session manager so app lifespan uses the cloned DB.
    api_dependencies.settings = Settings()  # type: ignore[call-arg]
    api_dependencies.sessionmanager = SessionManager()

    yield
    monkeypatch.undo()


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client_receive = fixture(_mqtt_client)
mqtt_client_send = fixture(_mqtt_client)
mqtt_client_external = fixture(_mqtt_client)


@fixture
async def sessionmanager(settings: Settings):
    manager = SessionManager()
    manager.initialize(settings.pg_url)
    yield manager
    await manager.close()


@fixture(autouse=True)
async def reset_mutable_tables(sessionmanager: SessionManager):
    async with sessionmanager.connect() as connection:
        await connection.execute(text("DELETE FROM loads.reference_values"))
        await connection.execute(text("DELETE FROM loads.load_case_mappings"))
        await connection.execute(text("DELETE FROM loads.load_cases"))


class LoadCaseFactory(DictFactory):
    id = LazyFunction(lambda: str(uuid4()))
    name = Sequence(lambda n: f"it-case-{n}")
    awa = 30.0
    aws = 22.0
    sail_set_id = 1


class LoadCaseMappingFactory(DictFactory):
    load_case_id = LazyFunction(lambda: str(uuid4()))
    awa_range_id = "upwind"
    aws_range_id = 1
    sail_set_id = 1


class ReferenceValueFactory(DictFactory):
    load_case_id = LazyFunction(lambda: str(uuid4()))
    variable_key = "main-sheet-load"
    alarm_low = None
    warning_low = None
    target = 9.6
    warning_high = 13.5
    alarm_high = 15.0


class ScenarioFactory:
    def __init__(self, manager: SessionManager):
        self._manager = manager

    async def _get_sail_set_id(self, sails: list[str]) -> int:
        sails_param = bindparam("sails", sorted(sails), type_=ARRAY(TEXT))
        async with self._manager.session() as session:
            result = await session.execute(
                select(SailSetsCombined.id).where(SailSetsCombined.sails == sails_param)
            )
            sail_set_id = result.scalar_one_or_none()
            if sail_set_id is None:
                raise ValueError(f"No sail_set found for sails={sorted(sails)}")
            return sail_set_id

    async def _get_aws_range_id(self, aws_range: str) -> int:
        async with self._manager.session() as session:
            result = await session.execute(
                select(AwsRanges.id).where(
                    AwsRanges.aws_range == text(f"'{aws_range}'::numrange")
                )
            )
            aws_range_id = result.scalar_one_or_none()
            if aws_range_id is None:
                raise ValueError(f"No aws_range found for range={aws_range}")
            return aws_range_id

    async def create_load_case(
        self,
        *,
        name: str,
        awa: float,
        aws: float,
        sails: list[str],
    ) -> str:
        sail_set_id = await self._get_sail_set_id(sails)
        payload = LoadCaseFactory.build(
            name=name, awa=awa, aws=aws, sail_set_id=sail_set_id
        )

        async with self._manager.session() as session:
            session.add(LoadCases(**payload))

        return payload["id"]

    async def map_load_case(
        self,
        *,
        load_case_id: str,
        awa_range_id: str,
        aws_range: str,
        sails: list[str],
    ) -> None:
        aws_range_id = await self._get_aws_range_id(aws_range)
        sail_set_id = await self._get_sail_set_id(sails)
        payload = LoadCaseMappingFactory.build(
            load_case_id=load_case_id,
            awa_range_id=awa_range_id,
            aws_range_id=aws_range_id,
            sail_set_id=sail_set_id,
        )

        async with self._manager.session() as session:
            session.add(LoadCaseMappings(**payload))

    async def create_reference_value(
        self,
        *,
        load_case_id: str,
        variable_key: str,
        alarm_low: float | None = None,
        warning_low: float | None = None,
        target: float | None = None,
        warning_high: float | None = None,
        alarm_high: float | None = None,
    ) -> None:
        payload = ReferenceValueFactory.build(
            load_case_id=load_case_id,
            variable_key=variable_key,
            alarm_low=alarm_low,
            warning_low=warning_low,
            target=target,
            warning_high=warning_high,
            alarm_high=alarm_high,
        )
        async with self._manager.session() as session:
            session.add(ReferenceValues(**payload))

    async def create_case_with_mapping(
        self,
        *,
        name: str,
        awa: float,
        aws: float,
        sails: list[str],
        awa_range_id: str,
        aws_range: str,
    ) -> str:
        load_case_id = await self.create_load_case(
            name=name, awa=awa, aws=aws, sails=sails
        )
        await self.map_load_case(
            load_case_id=load_case_id,
            awa_range_id=awa_range_id,
            aws_range=aws_range,
            sails=sails,
        )
        return load_case_id

    async def seed_graphql_reference_defaults(self) -> None:
        default_sails = ["full-main", "full-mizzen", "blade"]
        load_case_id = await self.create_case_with_mapping(
            name="graphql-default-upwind-20-25",
            awa=35,
            aws=22,
            sails=default_sails,
            awa_range_id="upwind",
            aws_range="[20,25)",
        )
        await self.create_reference_value(
            load_case_id=load_case_id,
            variable_key="main-sheet-load",
            target=9.6,
            warning_high=13.5,
            alarm_high=15.0,
        )
        await self.create_reference_value(
            load_case_id=load_case_id,
            variable_key="main-runner-load",
            target=17.3,
            warning_high=23.76,
            alarm_high=26.4,
        )

    async def seed_mutation_target_cases(self) -> None:
        sails = ["full-main", "full-mizzen"]
        await self.create_case_with_mapping(
            name="mutation-upwind-0-10",
            awa=8,
            aws=5,
            sails=sails,
            awa_range_id="upwind",
            aws_range="[0,10)",
        )
        await self.create_case_with_mapping(
            name="mutation-reaching-0-10",
            awa=70,
            aws=5,
            sails=sails,
            awa_range_id="reaching",
            aws_range="[0,10)",
        )
        await self.create_case_with_mapping(
            name="mutation-upwind-10-15",
            awa=10,
            aws=12,
            sails=sails,
            awa_range_id="upwind",
            aws_range="[10,15)",
        )
        await self.create_case_with_mapping(
            name="mutation-reaching-10-15",
            awa=75,
            aws=12,
            sails=sails,
            awa_range_id="reaching",
            aws_range="[10,15)",
        )

    async def seed_sentinel_reference(self, target: float = 777.77) -> None:
        load_case_id = await self.create_case_with_mapping(
            name="fixture-sentinel",
            awa=90,
            aws=35,
            sails=["full-main", "full-mizzen", "blade"],
            awa_range_id="reaching",
            aws_range="[30,40)",
        )
        await self.create_reference_value(
            load_case_id=load_case_id,
            variable_key="main-sheet-load",
            target=target,
        )


@fixture
def scenario_factory(sessionmanager: SessionManager) -> ScenarioFactory:
    return ScenarioFactory(sessionmanager)


@fixture
async def async_client():
    if api_dependencies.sessionmanager._engine is not None:
        await api_dependencies.sessionmanager.close()

    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://test"
        ) as client:
            yield client
