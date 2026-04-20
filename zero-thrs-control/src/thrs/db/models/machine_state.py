from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from thrs.input_output.alarms import Severity


class MachineStateIssue(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    severity_level: Severity
    issue_details: str | None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MachineStateEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    event_name: str
    event_details: str | None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MachineStateTransition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    trigger_name: str
    condition_name: str
    state_from: str
    state_to: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MachineStateGenericUpdate(SQLModel, table=False):
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    data_container_name: str
    parameters_from: str | None
    parameters_to: str
    parameters_diff: str | None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MachineStateParametersUpdate(MachineStateGenericUpdate, table=True): ...


class MachineStateControlValue(MachineStateGenericUpdate, table=True): ...
