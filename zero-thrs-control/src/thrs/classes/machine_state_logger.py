from enum import Enum
import json
from typing import Any, Literal, NoReturn, Type

from sqlmodel import SQLModel, Session
from thrs.classes import database
from thrs.db.models.machine_state import (
    MachineStateControlValue,
    MachineStateEvent,
    MachineStateIssue,
    MachineStateGenericUpdate,
    MachineStateParametersUpdate,
    MachineStateTransition,
)
from thrs.input_output.alarms import Severity
from thrs.input_output.base import ThrsValues
from thrs.utils.list import ensure_list
from thrs.utils.model import get_model_from_to_diff


class MachineStateValuesType(Enum):
    PARAMETERS = "parameters"
    CONTROL = "control"


class MachineStateLogger:
    """Provide direct log methods for the state machine, saving to the database."""

    def __init__(self) -> None:
        self.create_machinestate_tables()

    def log_event(self, event: MachineStateEvent):
        self._log_model(event)

    def log_transition(self, transition_change: MachineStateTransition):
        self._log_model(transition_change)

    def log_state_update(
        self, parameter: MachineStateParametersUpdate | MachineStateControlValue
    ):
        self._log_model(parameter)

    def log_alarm(self, alarm_name: str, severity: Severity, message: str):
        self.log_issue(
            MachineStateIssue(
                control_name=alarm_name,
                severity_level=severity,
                issue_details=message,
            )
        )

    def log_warning(self, message: str):
        self.log_issue(
            MachineStateIssue(
                control_name="Warning",
                severity_level=Severity.WARNING,
                issue_details=message,
            )
        )

    def log_issue(self, issue: MachineStateIssue):
        self._log_model(issue)

    def _log_model(self, model: SQLModel):
        try:
            with Session(database.db.engine) as session:
                session.add(model)
                session.commit()
        except Exception as e:
            print(f"Failed to log model {model}: {e}")
            # raise e

    def create_machinestate_tables(self):
        MachineStateIssue.metadata.create_all(database.db.engine)
        MachineStateTransition.metadata.create_all(database.db.engine)
        MachineStateParametersUpdate.metadata.create_all(database.db.engine)
        MachineStateControlValue.metadata.create_all(database.db.engine)
        MachineStateEvent.metadata.create_all(database.db.engine)


class MachineStateLoggingService:
    """Service to be inherited by a state machine using class. Providing logging capabilities for state transitions (and the triggered condition(s)), changing THRS values, custom events and issues."""

    state: str  # Set by transitions logic
    _initialized: bool = False

    @property
    def machinestate_logger(self) -> MachineStateLogger:
        self.ensure_init()
        return self._machinestate_logger

    def ensure_init(self):
        """Ensures that the logger is initialized. __init__ is not used to avoid issues with multiple inheritance and to allow for lazy initialization."""
        if self._initialized:
            return
        self._initialized = True

        self._machinestate_logger: MachineStateLogger = MachineStateLogger()

        self._last_state: str = "Unknown"
        self._last_evaluated_conditions = []
        self._last_trigger_name: str | None = None

    def setup_transition_tracking(self, transitions: list[dict[str, Any]]):
        """Wraps the trigger methods of the transitions to track the last triggered transition."""
        for t in transitions:
            trigger_name = t["trigger"]
            trigger_method = getattr(self, trigger_name)

            def wrapper(trigger_method=trigger_method, trigger_name=trigger_name):
                def _inner(*a, **kw):
                    self._last_trigger_name = trigger_name
                    return trigger_method(*a, **kw)

                return _inner

            setattr(self, trigger_name, wrapper())

    def setup_condition_tracking(self, transitions: list[dict[str, Any]]):
        """Wraps the condition methods to track the last created conditions."""

        def make_wrapper(func, condition_name):
            def wrapper(*a, **kw):
                result = func(*a, **kw)
                if result:
                    self._last_evaluated_conditions.append(condition_name)
                return result

            return wrapper

        for transition in transitions:
            if "conditions" in transition:
                conditions = ensure_list(transition["conditions"])

                wrapped = []
                for c in conditions:
                    if callable(c):
                        name = c.__name__
                        func = c
                    else:
                        name = c
                        func = getattr(self, c)

                    wrapped.append(make_wrapper(func, name))

                transition["conditions"] = wrapped

    def _before_log(self, sensor_values):
        """Called before the transition is made, to track the last state."""
        self._last_state = self.state

    def _after_log(self, sensor_values):
        """Called after the transition is made, to log the transition and reset the tracked conditions."""
        condition_name: str = (
            ", ".join(self._last_evaluated_conditions)
            if self._last_evaluated_conditions
            else "Unknown"
        )

        transition_change = MachineStateTransition(
            control_name=self.__class__.__name__,
            trigger_name=self._last_trigger_name or "Unknown",
            condition_name=condition_name,
            state_from=self._last_state,
            state_to=self.state,
        )
        self.machinestate_logger.log_transition(transition_change)
        self._last_evaluated_conditions = []

    def log_and_raise_warning(self, message: str) -> NoReturn:
        """Logs a warning and raises it as an exception."""
        self.log_issue(message, Severity.WARNING)
        raise Warning(message)

    def log_model_initial_state(
        self, initial_state: ThrsValues, values_type: MachineStateValuesType
    ):
        """Logs the initial state of the parameter or control values when they are first created. Not saving a from state and difference."""

        cls: Type[MachineStateGenericUpdate] = (
            MachineStateControlValue
            if values_type == MachineStateValuesType.CONTROL
            else MachineStateParametersUpdate
        )

        parameters_log: MachineStateGenericUpdate = cls(
            control_name=self.__class__.__name__,
            data_container_name=type(initial_state).__name__,
            parameters_from=None,
            parameters_to=initial_state.model_dump_json(),
            parameters_diff=None,
        )

        self.machinestate_logger.log_state_update(parameters_log)

    def log_thrsvalues_on_differ(
        self,
        values_from: ThrsValues,
        values_to: ThrsValues,
        values_type: MachineStateValuesType,
    ):
        """Logs only the changes in the thrs values if they differ, accompanied by the full from and to values."""
        if type(values_from) is not type(values_to):
            raise ValueError(
                f"From and To values must be of the same type for comparison, got From: {type(values_from)} and To: {type(values_to)}"
            )

        model_to: dict[str, Any] = values_from.model_dump()
        model_from: dict[str, Any] = values_to.model_dump()

        if model_to != model_from:
            model_diff: dict[str, dict[Literal["from", "to"], Any]] = (
                get_model_from_to_diff(model_to, model_from)
            )

            cls: Type[MachineStateGenericUpdate] = (
                MachineStateControlValue
                if values_type == MachineStateValuesType.CONTROL
                else MachineStateParametersUpdate
            )

            parameters_log: MachineStateGenericUpdate = cls(
                control_name=self.__class__.__name__,
                data_container_name=type(values_from).__name__,
                parameters_from=values_from.model_dump_json(),
                parameters_to=values_to.model_dump_json(),
                parameters_diff=json.dumps(model_diff),
            )

            self.machinestate_logger.log_state_update(parameters_log)

    def log_issue(self, message: str, severity: Severity):
        self.machinestate_logger.log_issue(
            MachineStateIssue(
                control_name=self.__class__.__name__,
                severity_level=severity,
                issue_details=message,
            )
        )
