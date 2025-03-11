from datetime import timedelta
from types import TracebackType
from typing import Any, Callable, Iterable, Self

from fmpy import extract, read_model_description
from fmpy.fmi2 import FMU2Slave
from fmpy.model_description import ModelDescription
from pydantic import BaseModel

from input_output.base import ThrsModel
from simulation.input_output import SimulationInputs


def _var_mapper(
    model_description: ModelDescription,
) -> Callable[[Iterable[str]], list[int]]:
    _var_name_to_ref = {
        variable.name: variable.valueReference
        for variable in model_description.modelVariables
    }
    return lambda names: [_var_name_to_ref[name] for name in names]


class Fmu[ControlValues: ThrsModel, SensorValues: ThrsModel, SimulationOutputs]:
    def __init__(
        self,
        file: str,
        parameters: BaseModel,
        sensor_values_cls: type[SensorValues],
        simulation_outputs_cls: type[SimulationOutputs],
        solver_step_size: timedelta,
    ):
        model_description = read_model_description(file)
        temp_unzip_dir = extract(file)

        self._fmu = FMU2Slave(
            guid=model_description.guid,
            unzipDirectory=temp_unzip_dir,
            modelIdentifier=model_description.coSimulation.modelIdentifier,
        )

        self._var_mapper = _var_mapper(model_description)
        self._time = 0.0
        self._step_size = solver_step_size.total_seconds()
        self._sensors_cls = sensor_values_cls
        self._simulation_outputs_cls = simulation_outputs_cls
        self._fmu.instantiate()
        self._fmu.setupExperiment(startTime=0.0)
        self._fmu.enterInitializationMode()
        self._fmu.exitInitializationMode()
        parameter_values = parameters.model_dump()
        self._fmu.setReal(
            self._var_mapper(parameter_values.keys()),
            parameter_values.values(),
        )

        output_names = self._sensors_cls.model_fields.keys()
        outputs = self._fmu.getReal(self._var_mapper(output_names))
        self._initial_values = self._sensors_cls(**dict(zip(output_names, outputs)))

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self._fmu.terminate()
        self._fmu.freeInstance()
        if value is not None:
            raise value
        return True

    def tick(
        self,
        control_values: ControlValues,
        simulation_inputs: SimulationInputs,
        duration: timedelta,
    ) -> tuple[SensorValues, SimulationOutputs]:
        stop = self._time + duration.total_seconds()

        control_dict = control_values.model_dump()
        simulation_inputs_dict = simulation_inputs.model_dump()

        self._fmu.setReal(
            self._var_mapper(control_dict.keys())
            + self._var_mapper(simulation_inputs_dict.keys()),
            list(control_dict.values()) + list(simulation_inputs_dict.values()),
        )

        while self._time < stop:
            self._fmu.doStep(
                currentCommunicationPoint=self._time,
                communicationStepSize=self._step_size,
            )

            self._time += self._step_size

        output_names = self._sensors_cls.model_fields.keys()
        outputs = self._fmu.getReal(self._var_mapper(output_names))
        output_dict = dict(zip(output_names, outputs))
        return self._sensors_cls(**output_dict), self._simulation_outputs_cls(
            **output_dict
        )

    @property
    def solver_time(self):
        return self._time
