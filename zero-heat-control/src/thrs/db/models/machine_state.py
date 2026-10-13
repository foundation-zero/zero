from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from thrs.input_output.alarms import Severity


class MachineStateModelBase(SQLModel):
    __table_args__ = {"schema": "thrs"}


class MachineStateIssue(MachineStateModelBase, table=True):
    __tablename__ = "machinestate_issue"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    severity_level: Severity = Field(
        sa_column=Column(
            SAEnum(Severity, native_enum=False, length=None), nullable=False
        )
    )
    issue_details: str | None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class MachineStateEvent(MachineStateModelBase, table=True):
    __tablename__ = "machinestate_event"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    event_name: str
    event_details: str | None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class MachineStateTransition(MachineStateModelBase, table=True):
    __tablename__ = "machinestate_transition"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    trigger_name: str
    condition_name: str
    state_from: str
    state_to: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class MachineStateParametersUpdate(MachineStateModelBase, table=True):
    __tablename__ = "machinestate_parameters"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    data_container_name: str
    parameters_from: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    parameters_to: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    parameters_diff: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
