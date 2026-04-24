from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from thrs.input_output.alarms import Severity


class MachineStateModelBase(SQLModel):
    __table_args__ = {"schema": "thrs"}


class MachineStateIssue(MachineStateModelBase, table=True):
    __tablename__ = "machinestate_issue"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    severity_level: Severity
    issue_details: str | None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MachineStateEvent(MachineStateModelBase, table=True):
    __tablename__ = "machinestate_event"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    event_name: str
    event_details: str | None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MachineStateTransition(MachineStateModelBase, table=True):
    __tablename__ = "machinestate_transition"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    trigger_name: str
    condition_name: str
    state_from: str
    state_to: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MachineStateParametersUpdate(MachineStateModelBase, table=True):
    __tablename__ = "machinestate_parameters"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    control_name: str
    data_container_name: str
    parameters_from: str | None
    parameters_to: str
    parameters_diff: str | None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
