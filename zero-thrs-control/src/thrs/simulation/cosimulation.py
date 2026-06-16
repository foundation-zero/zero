import dataclasses
from dataclasses import dataclass
from datetime import timedelta
from functools import reduce
from operator import or_
from types import TracebackType
from typing import Any, Self

from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues
from thrs.input_output.fmu_mapping import build_fmu_key_mapping
from thrs.simulation.fmu import Fmu


@dataclass
class Coupling:
    src_component: str
    src_field: str
    dest_component: str
    dest_field: str
    initial_value: Any


@dataclass
class CoSimulationParticipant[
    S: ThrsValues,
    C: ThrsValues,
    I: SimulationInputs,
    O: SimulationValues,
]:
    """An FMU, its schemas, and how it relates to other FMU and initial boundary conditions."""

    fmu: Fmu
    sensor_values_cls: type[C]
    control_values_cls: type[S]
    simulation_inputs_cls: type[I]
    simulation_outputs_cls: type[O]

    couplings: list[Coupling]

    fmu_key_input_mapping: dict[tuple[str, str], str] = dataclasses.field(init=False)
    fmu_key_output_mapping: dict[tuple[str, str], str] = dataclasses.field(init=False)

    def __post_init__(self):
        self.fmu_key_input_mapping = {
            **build_fmu_key_mapping(self.control_values_cls, fmu_only=False),
            **build_fmu_key_mapping(self.simulation_inputs_cls, fmu_only=False),
        }
        self.fmu_key_output_mapping = {
            **build_fmu_key_mapping(self.simulation_outputs_cls, fmu_only=False),
            **build_fmu_key_mapping(self.sensor_values_cls, fmu_only=False),
        }

        for coupling in self.couplings:
            if (
                coupling.dest_component,
                coupling.dest_field,
            ) not in self.fmu_key_input_mapping:
                raise ValueError(
                    f"The coupling destination '{coupling.dest_component}.{coupling.dest_field}' is not part of the input mapping {self.fmu_key_input_mapping}."
                )


class CoSimulationMaster:
    """Connect multiple FMU, behaving like a single FMU."""

    def __init__(self, participants: list[CoSimulationParticipant]):
        self._participants = participants
        self._previous_outputs: dict[str, Any] = {}
        self._compiled_couplings: list[dict[str, str]] = []

        self._fmu_key_output_mapping = reduce(
            or_,
            (participant.fmu_key_output_mapping for participant in self._participants),
        )

        self._set_initial_conditions()
        self._compile_couplings()

    def _set_initial_conditions(self):
        self._previous_outputs = {
            self._fmu_key_output_mapping[
                (coupling.src_component, coupling.src_field)
            ]: coupling.initial_value
            for participant in self._participants
            for coupling in participant.couplings
        }

    def _compile_couplings(self):
        def _src_fmu_key(coupling):
            src_fmu_key = self._fmu_key_output_mapping.get(
                (
                    coupling.src_component,
                    coupling.src_field,
                )
            )
            if src_fmu_key is None:
                raise ValueError(
                    f"The coupling source {coupling.src_component}.{coupling.src_field} is not found in any participant's output mapping."
                )
            return src_fmu_key

        self._compiled_couplings = [
            {
                participant.fmu_key_input_mapping[
                    (coupling.dest_component, coupling.dest_field)
                ]: _src_fmu_key(coupling)
                for coupling in participant.couplings
            }
            for participant in self._participants
        ]

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        for participant in self._participants:
            participant.fmu.__exit__(type_, value, traceback)
        return True

    def tick(self, inputs: dict[str, Any], duration: timedelta) -> dict[str, Any]:
        current_outputs: dict[str, Any] = {}

        for participant, coupling in zip(self._participants, self._compiled_couplings):
            # filter the inputs for the current participant
            participant_inputs = {
                key: value
                for key, value in inputs.items()
                if key in participant.fmu_key_input_mapping.values()
            }

            # inject previous outputs from other participants based on the coupling
            for dest_fmu_key, src_fmu_key in coupling.items():
                if dest_fmu_key in participant_inputs:
                    raise ValueError(
                        f"Input '{dest_fmu_key}' for participant '{participant}' is being set both directly and via coupling from '{src_fmu_key}'."
                    )
                participant_inputs[dest_fmu_key] = self._previous_outputs[src_fmu_key]

            participant_outputs = participant.fmu.tick(participant_inputs, duration)
            current_outputs.update(participant_outputs)

        self._previous_outputs = current_outputs
        return current_outputs

    @property
    def solver_time(self) -> float:
        return self._participants[-1].fmu.solver_time
