"""The behaviour of the THRS control API, as data.

What a client can rely on beyond the shapes of the models: the query fields
and sections, how mutations are named, how long a write waits for the
controller to confirm it and what it says when that fails, and which simulation
directives are allowed from which status. Both the API implementation
(``thrs.graphql``) and the published contract (``thrs.spec``) read it from
here, so neither can drift from the other.
"""

from dataclasses import dataclass

from thrs.runtime.messages import (
    IncomingMessage,
    PauseMessage,
    PlayMessage,
    SimulationStatus,
    StepMessage,
)

# --- Query surface -----------------------------------------------------------

MODULES_QUERY_FIELD = "modules"
MODULES_TYPE_NAME = "ControlModules"
SIMULATION_QUERY_FIELD = "simulation"
SIMULATION_STATE_TYPE_NAME = "SimulationState"
SIMULATION_INPUTS_UNION = "SimulationInputsType"
SIMULATION_OUTPUTS_UNION = "SimulationOutputsType"

# The sections of a module (`modules.<module>.<section>`), by python name.
SENSOR_VALUES_SECTION = "sensor_values"
CONTROL_VALUES_SECTION = "control_values"
PARAMETERS_SECTION = "parameters"
CONTROLLER_STATE_SECTION = "controller_state"
CONTROL_MODE_SECTION = "control_mode"
# The sections of a simulation (`simulation.<section>`).
INPUTS_SECTION = "inputs"
OUTPUTS_SECTION = "outputs"
# The fields of the simulation state.
STATUS_FIELD = "status"
TIME_FIELD = "time"

# The switching control mode (`controlMode { automatic automaticMode {...} }`).
AUTOMATIC_FLAG_FIELD = "automatic"
AUTOMATIC_MODE_FIELD = "automatic_mode"

# --- Mutations ---------------------------------------------------------------

# Python names of the mutations; the GraphQL names follow from
# `thrs.spec.naming.field_name`.
CONTROL_MUTATION_NAME = "{module}_control_set_{field}"
PARAMETER_MUTATION_NAME = "{module}_parameter_set_{field}"
SIMULATION_INPUT_MUTATION_NAME = "{mode}_simulation_set_{field}"
AUTOMATION_MODE_MUTATION_NAME = "{module}_set_automation_mode"
SIMULATION_DIRECTIVE_MUTATION_NAME = "simulation_{directive}"

# The single argument of a set mutation, and of the automation-mode switch.
VALUE_ARGUMENT = "value"
AUTOMATIC_ARGUMENT = "automatic"

# Seconds a write waits for the controller (or simulator) to echo the change.
WAIT_TIMEOUT = 5

NO_CONTROL_VALUES_ERROR = "No control values available to modify"
NO_PARAMETERS_ERROR = "No parameters available to update"
NO_SIMULATION_INPUTS_ERROR = "No simulation inputs available to modify"


def timeout_error(subject: str) -> str:
    """The error a write raises when ``subject`` is not echoed in time."""
    return f"Timeout when setting {subject}"


CONTROL_VALUES_TIMEOUT_ERROR = timeout_error("control values")
PARAMETERS_TIMEOUT_ERROR = timeout_error("parameters")
AUTOMATION_MODE_TIMEOUT_ERROR = timeout_error("automation mode")
SIMULATION_INPUTS_TIMEOUT_ERROR = timeout_error("simulation inputs")


# --- Simulation directives ---------------------------------------------------


@dataclass(frozen=True)
class SimulationDirective:
    """How the API guards one simulation directive: the statuses it may be
    issued from, the status it then waits for, and the exact errors otherwise."""

    message: type[IncomingMessage]
    allowed_from: tuple[SimulationStatus, ...]
    expect_status: SimulationStatus
    precondition_error: str
    missing_error: str


PLAY = SimulationDirective(
    PlayMessage,
    allowed_from=("available", "running"),
    expect_status="running",
    precondition_error="Can only play an available or running simulation",
    missing_error="No simulation status available, cannot play",
)
PAUSE = SimulationDirective(
    PauseMessage,
    allowed_from=("running",),
    expect_status="available",
    precondition_error="Can only pause a running simulation",
    missing_error="No simulation status available, cannot pause",
)
STEP = SimulationDirective(
    StepMessage,
    allowed_from=("available",),
    expect_status="stepping",
    precondition_error="Can only step an available simulation",
    missing_error="No simulation status available, cannot step",
)

SIMULATION_DIRECTIVES = (PLAY, PAUSE, STEP)
