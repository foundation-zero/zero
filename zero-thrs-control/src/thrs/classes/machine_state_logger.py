import asyncio
import json
import logging
import warnings
from abc import abstractmethod
from enum import Enum
from functools import partial, wraps
from typing import Any, Coroutine, Literal

from sqlmodel import SQLModel
from transitions import Machine, State

from thrs.classes.control import Control
from thrs.classes.database import PostgresDatabase
from thrs.db.models.machine_state import (
    MachineStateEvent,
    MachineStateIssue,
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

    def __init__(self, postgres_db: PostgresDatabase):
        self.postgres_db: PostgresDatabase = postgres_db
        self._pending_tasks: set[asyncio.Task[None]] = set()

    def log_event(self, event: MachineStateEvent):
        self._log_model(event)

    def log_transition(self, transition_change: MachineStateTransition):
        self._log_model(transition_change)

    def log_parameters(self, parameter: MachineStateParametersUpdate):
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
        """Log a model to the database asynchronously."""
        self._run_async(self._log_model_async(model))

    def _run_async(self, coroutine: Coroutine):
        """Run a non-blocking coroutine in the current event loop, or create a new loop if none exists."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Fallback for when there is no running event loop, e.g., in a synchronous context
            asyncio.run(coroutine)
            return

        # Coroutine will run when the loop is idle, without blocking the current thread
        task: asyncio.Task[None] = loop.create_task(coroutine)
        self._pending_tasks.add(task)
        task.add_done_callback(self._on_task_done)

    def _on_task_done(self, task: asyncio.Task[None]) -> None:
        """Crash the application if a logging task failed, instead of continuing silently."""
        self._pending_tasks.discard(task)
        if task.cancelled():
            return
        exception: BaseException | None = task.exception()
        if exception is not None:
            task.get_loop().stop()
            raise exception

    async def wait_for_pending_tasks(self, timeout: float | None = 10.0) -> None:
        """Wait until all in-flight logging tasks have finished. Call on app shutdown."""
        if not self._pending_tasks:
            return
        await asyncio.wait(self._pending_tasks, timeout=timeout)

    async def _log_model_async(self, model: SQLModel):
        async with self.postgres_db.session_factory() as session:
            session.add(model)
            await session.commit()


class StateLogger:
    @abstractmethod
    def create_logged_state_machine(
        self,
        control: "Control",
        transitions: list[dict],
        states: list[State],
        initial: str,
    ) -> Machine: ...

    @property
    def machinestate_logger(self) -> MachineStateLogger: ...

    # TODO: Delete when rebased to main
    @abstractmethod
    def clone_for_module(self) -> "StateLogger": ...

    def log_issue(self, message: str, severity: Severity): ...
    def log_event(self, event: MachineStateEvent): ...

    async def shutdown(self) -> None:
        """Drain pending logging tasks and release resources. Should be called on app shutdown."""

    @abstractmethod
    def log_parameters_on_change(
        self,
        values_from: ThrsValues,
        values_to: ThrsValues,
    ): ...
    @abstractmethod
    def log_parameters_initial_state(self, initial_state: ThrsValues): ...
    @abstractmethod
    def log_warning(self, message: str): ...

    @staticmethod
    def log_parameters(func):
        def wrapper(self: "Control", parameters: "ThrsValues"):
            if hasattr(self, "state_logger") and self.state_logger:
                self.state_logger.log_parameters_on_change(
                    values_from=self._parameters,
                    values_to=parameters,
                )
            self._parameters = parameters
            return func(self, parameters)

        return wrapper

    @staticmethod
    def log_warnings(func):
        @wraps(func)
        def wrapper(self: "Control", *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Warning as e:
                if hasattr(self, "state_logger") and self.state_logger:
                    self.state_logger.log_warning(str(e))
                raise

        return wrapper

    @staticmethod
    def log_alarms(func):
        @wraps(func)
        def wrapper(self: "Control", *args, **kwargs):
            result = None
            if hasattr(self, "state_logger") and self.state_logger:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    result = func(self, *args, **kwargs)
                    for warning in w:
                        if isinstance(warning.message, Warning):
                            self.state_logger.log_issue(
                                message=str(warning.message), severity=Severity.ALARM
                            )
            else:
                result = func(self, *args, **kwargs)
            return result

        return wrapper


class MachineStateLoggingServiceNoop(StateLogger):
    """A no-op version of the MachineStateLoggingService, for when logging is not desired."""

    def create_logged_state_machine(
        self,
        control: "Control",
        transitions: list[dict],
        states: list[State],
        initial: str,
    ) -> Machine:
        """Creates a MachineStateConstruct with the given states, transitions and initial state. The construct can then be applied to a control to enable logging."""

        return Machine(
            model=control,
            states=states,
            transitions=transitions,
            initial=initial,
        )

    def clone_for_module(self) -> "StateLogger":
        return self


class MachineStateLoggingService(StateLogger):
    """Service to be inherited by a state machine using class. Providing logging capabilities for state transitions (and the triggered condition(s)), changing THRS values, custom events and issues."""

    _initialized: bool = False

    def __init__(self, postgres_db: PostgresDatabase):
        self._machinestate_logger: MachineStateLogger = MachineStateLogger(postgres_db)
        self.last_state: str = "Unknown"
        self.last_trigger_name: str | None = "Unknown"
        self.last_evaluated_conditions: list[str] = []

    def clone_for_module(self) -> "StateLogger":
        clone = MachineStateLoggingService(self.machinestate_logger.postgres_db)
        clone._machinestate_logger = self._machinestate_logger
        return clone

    async def shutdown(self) -> None:
        """Wait for in-flight logging tasks, then dispose the database engine."""
        await self._machinestate_logger.wait_for_pending_tasks()
        await self._machinestate_logger.postgres_db.close()

    def create_logged_state_machine(
        self,
        control: "Control",
        transitions: list[dict],
        states: list[State],
        initial: str,
    ) -> Machine:
        """Creates a MachineStateConstruct with the given states, transitions and initial state. The construct can then be applied to a control to enable logging."""

        self.setup_condition_tracking(
            transitions, control
        )  # Setup before Machine creation

        machine = Machine(
            model=control,
            states=states,
            transitions=transitions,
            initial=initial,
        )

        self.setup_transition_tracking(transitions, control)

        machine.before_state_change = partial(self._before_log, control)
        machine.after_state_change = partial(self._after_log, control)

        return machine

    def setup_transition_tracking(
        self, transitions: list[dict[str, Any]], control: "Control"
    ):
        """Wraps the trigger methods of the transitions to track the last triggered transition."""
        for t in transitions:
            trigger_name = t["trigger"]
            trigger_method = getattr(control, trigger_name)

            def wrapper(trigger_method=trigger_method, trigger_name=trigger_name):
                def _inner(*a, **kw):
                    self.last_trigger_name = trigger_name
                    return trigger_method(*a, **kw)

                return _inner

            setattr(control, trigger_name, wrapper())

    def setup_condition_tracking(
        self, transitions: list[dict[str, Any]], control: "Control"
    ):
        """Wraps the condition methods to track the last created conditions."""

        def make_wrapper(func, condition_name):
            def wrapper(*a, **kw):
                result = func(*a, **kw)
                if result:
                    self.last_evaluated_conditions.append(condition_name)
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
                        func = getattr(control, c)
                    wrapped.append(make_wrapper(func, name))

                transition["conditions"] = wrapped

    @property
    def machinestate_logger(self) -> MachineStateLogger:
        return self._machinestate_logger

    def _before_log(self, control: "Control", sensor_values):
        """Called before the transition is made, to track the last state."""
        self.last_state = control.state

    def _after_log(self, control: "Control", sensor_values):
        """Called after the transition is made, to log the transition and reset the tracked conditions."""
        condition_name: str = (
            ", ".join(self.last_evaluated_conditions)
            if self.last_evaluated_conditions
            else "Unknown"
        )
        transition_change = MachineStateTransition(
            control_name=control.__class__.__name__,
            trigger_name=self.last_trigger_name or "Unknown",
            condition_name=condition_name,
            state_from=self.last_state,
            state_to=control.state,
        )
        self.machinestate_logger.log_transition(transition_change)
        self.last_evaluated_conditions = []

    def log_warning(self, message: str):
        self.log_issue(message, Severity.WARNING)

    def log_parameters_initial_state(self, initial_state: ThrsValues):
        """Logs the initial state of the parameter values when they are first created. Not saving a from state and difference."""

        self.machinestate_logger.log_parameters(
            MachineStateParametersUpdate(
                control_name=self.__class__.__name__,
                data_container_name=type(initial_state).__name__,
                parameters_from=None,
                parameters_to=initial_state.model_dump_json(),
                parameters_diff=None,
            )
        )

    def log_parameters_on_change(
        self,
        values_from: ThrsValues,
        values_to: ThrsValues,
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

            self.machinestate_logger.log_parameters(
                MachineStateParametersUpdate(
                    control_name=self.__class__.__name__,
                    data_container_name=type(values_from).__name__,
                    parameters_from=values_from.model_dump_json(),
                    parameters_to=values_to.model_dump_json(),
                    parameters_diff=json.dumps(model_diff),
                )
            )

    def log_issue(self, message: str, severity: Severity):
        self.machinestate_logger.log_issue(
            MachineStateIssue(
                control_name=self.__class__.__name__,
                severity_level=severity,
                issue_details=message,
            )
        )

    def log_event(self, event: MachineStateEvent):
        self.machinestate_logger.log_event(event)
