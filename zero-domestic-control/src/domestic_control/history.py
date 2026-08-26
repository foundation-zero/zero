from abc import ABC, abstractmethod
from datetime import datetime
from itertools import groupby
from typing import Annotated, Any

from sqlalchemy import TextClause, func, select
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql.functions import _FunctionGenerator
from sqlmodel import Column, Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

_OPERATIONS: dict[Any, _FunctionGenerator] = {float: func.avg, bool: func.last_value}


class GreptimeLog(SQLModel, ABC):
    timestamp: Annotated[datetime, Field(primary_key=True)]

    @classmethod
    @abstractmethod
    def room_column(cls) -> Any: ...

    @classmethod
    def extra_columns(cls) -> list:
        return []

    @classmethod
    async def query(
        cls,
        engine: AsyncEngine,
        room_ids: list[str],
        start_time: datetime,
        end_time: datetime,
        period: TextClause,
    ):
        async with AsyncSession(engine) as session:
            operations = [
                fun(getattr(cls, field_name)).label(field_name)
                for field_name, field in cls.model_fields.items()
                if (fun := _OPERATIONS.get(field.annotation))
            ]
            time_col = func.date_bin(period, cls.timestamp).label("timestamp")
            statement = (
                select(cls.room_column(), *operations, *cls.extra_columns(), time_col)
                .where(cls.timestamp >= start_time, cls.timestamp <= end_time)  # type: ignore
                .where(cls.room_column().in_(room_ids))  # type: ignore
                .group_by(cls.room_column(), *cls.extra_columns(), time_col)
                .order_by(cls.room_column(), *cls.extra_columns(), time_col)
            )

            results = (await session.exec(statement)).all()  # type: ignore
            print(results)
            return {
                room_id: list(rows)
                for room_id, rows in groupby(
                    results, lambda row: getattr(row, cls.room_column().key)
                )
            }


class AcLog(GreptimeLog, table=True):
    __tablename__ = "domestic__ac"  # type: ignore

    id: str
    temperature_setpoint: float
    humidity_setpoint: float
    actual_temperature: float
    actual_humidity: float

    @classmethod
    def room_column(cls) -> str:
        return cls.id


class VentilationLog(GreptimeLog, table=True):
    __tablename__ = "domestic__ventilation"  # type: ignore

    id: str
    co2_setpoint: Annotated[float, Field(sa_column=Column("co_2_setpoint"))]
    actual_co2: Annotated[float, Field(sa_column=Column("actual_co_2"))]

    @classmethod
    def room_column(cls) -> str:
        return cls.id


class AmplifiersLog(GreptimeLog, table=True):
    __tablename__ = "domestic__amplifiers"  # type: ignore

    id: str
    on: bool

    @classmethod
    def room_column(cls) -> str:
        return cls.id


class BlindsLog(GreptimeLog, table=True):
    __tablename__ = "domestic__blinds"  # type: ignore

    id: str
    room_id: str
    level: float

    @classmethod
    def room_column(cls) -> str:
        return cls.room_id

    @classmethod
    def extra_columns(cls) -> list:
        return [cls.id]


class LightingGroupsLog(GreptimeLog, table=True):
    __tablename__ = "domestic__lighting_groups"  # type: ignore

    id: str
    room_id: str
    level: float

    @classmethod
    def room_column(cls) -> str:
        return cls.room_id

    @classmethod
    def extra_columns(cls) -> list:
        return [cls.id]
