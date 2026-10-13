import dataclasses
import operator
from collections.abc import Callable
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import timedelta
from functools import reduce
from typing import Any, Self

from thrs.input_output.base import ThrsValues
from thrs.input_output.fmu_mapping import build_fmu_key_mapping
from thrs.simulation.fmu import Fmu, FmuLike


@dataclass
class Coupling:
    src_component: str
    src_field: str
    dest_component: str
    dest_field: str
    initial_value: Any


@dataclass
class CoSimulationParticipant:
    """An FMU, its schemas, and how it relates to other FMU and initial boundary conditions."""

    fmu_getter: Callable[[], Fmu]
    sensor_values_clss: list[type[ThrsValues]]
    control_values_clss: list[type[ThrsValues]]
    simulation_inputs_cls: type[ThrsValues]
    simulation_outputs_cls: type[ThrsValues]

    couplings: list[Coupling]

    _fmu: Fmu | None = dataclasses.field(init=False, default=None, repr=False)
    fmu_key_input_mapping: dict[tuple[str, str], str] = dataclasses.field(init=False)
    fmu_key_output_mapping: dict[tuple[str, str], str] = dataclasses.field(init=False)

    def resolve_fmu(self) -> Fmu:
        if self._fmu is None:
            self._fmu = self.fmu_getter()
        return self._fmu

    @property
    def fmu(self) -> Fmu:
        return self.resolve_fmu()

    def __post_init__(self):
        self.fmu_key_input_mapping = reduce(
            operator.ior,
            [
                build_fmu_key_mapping(cls, fmu_only=False)
                for cls in [*self.control_values_clss, self.simulation_inputs_cls]
            ],
            {},
        )
        self.fmu_key_output_mapping = reduce(
            operator.ior,
            [
                build_fmu_key_mapping(cls, fmu_only=False)
                for cls in [*self.sensor_values_clss, self.simulation_outputs_cls]
            ],
            {},
        )

        for coupling in self.couplings:
            if (
                coupling.dest_component,
                coupling.dest_field,
            ) not in self.fmu_key_input_mapping:
                raise ValueError(
                    f"The coupling destination '{coupling.dest_component}.{coupling.dest_field}' is not part of the input mapping {self.fmu_key_input_mapping}."
                )


class CoSimulationMaster(ExitStack, FmuLike):
    """Connect multiple FMU, behaving like a single FMU."""

    def __init__(self, participants: list[CoSimulationParticipant]):
        self._participants = participants
        self._previous_outputs: dict[str, Any] = {}
        self._compiled_couplings: list[dict[str, str]] = []

        self.total_fmu_key_output_mapping = reduce(
            operator.ior,
            [participant.fmu_key_output_mapping for participant in self._participants],
            {},
        )

        self._set_initial_conditions()
        self._compile_couplings()
        super().__init__()

    def _set_initial_conditions(self):
        self._previous_outputs = {
            self.total_fmu_key_output_mapping[
                (coupling.src_component, coupling.src_field)
            ]: coupling.initial_value
            for participant in self._participants
            for coupling in participant.couplings
        }

    def _compile_couplings(self):
        def _src_fmu_key(coupling):
            src_fmu_key = self.total_fmu_key_output_mapping.get(
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
        super().__enter__()

        try:
            for participant in self._participants:
                self.enter_context(participant.resolve_fmu())
        except Exception:
            super().__exit__(None, None, None)
            raise

        return self

    def tick(self, inputs: dict[str, Any], duration: timedelta) -> dict[str, Any]:
        current_outputs: dict[str, Any] = {}

        for participant, coupling in zip(
            self._participants, self._compiled_couplings, strict=False
        ):
            # filter the inputs for the current participant
            direct_inputs = {
                key: value
                for key, value in inputs.items()
                if key in participant.fmu_key_input_mapping.values()
            }

            inputs_from_coupling = {
                dest_fmu_key: self._previous_outputs[src_fmu_key]
                for dest_fmu_key, src_fmu_key in coupling.items()
            }

            if duplicate_keys := set(direct_inputs) & set(inputs_from_coupling):
                raise ValueError(
                    f"Input keys {duplicate_keys} for participant '{participant}' are being set both directly and via coupling."
                )

            participant_inputs = {**direct_inputs, **inputs_from_coupling}

            participant_outputs = participant.resolve_fmu().tick(
                participant_inputs, duration
            )
            current_outputs.update(participant_outputs)

        self._previous_outputs = current_outputs
        return current_outputs

    @property
    def solver_time(self) -> float:
        return self._participants[-1].resolve_fmu().solver_time
