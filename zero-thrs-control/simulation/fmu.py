from collections.abc import Sequence
from datetime import timedelta
from types import TracebackType
from typing import Any, Callable, Iterable, Self
from fmpy import read_model_description, extract
from fmpy.model_description import ModelDescription
from fmpy.fmi2 import FMU2Slave
from pydantic import BaseModel


def _var_mapper(
    model_description: ModelDescription,
) -> Callable[[Iterable[str]], list[int]]:
    _var_name_to_ref = {
        variable.name: variable.valueReference
        for variable in model_description.modelVariables
    }
    return lambda names: [_var_name_to_ref[name] for name in names]


class Fmu[ControlValues: BaseModel, SensorValues: BaseModel]:
    def __init__(
        self,
        file: str,
        parameters: BaseModel,
        sensor_values_cls: type[SensorValues],
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
        self._fmu.instantiate()
        self._fmu.setupExperiment(startTime=0.0)
        self._fmu.enterInitializationMode()
        self._fmu.exitInitializationMode()
        parameter_values = parameters.model_dump()
        self._fmu.setReal(
            self._var_mapper(parameter_values.keys()),
            parameter_values.values(),
        )

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
        return True

    def tick(
        self,
        control_values: ControlValues,
        environmentals: dict[str, Any],
        duration: timedelta,
    ) -> SensorValues:
        stop = self._time + duration.total_seconds()

        control_dict = control_values.model_dump()

        self._fmu.setReal(
            self._var_mapper(control_dict.keys())
            + self._var_mapper(environmentals.keys()),
            list(control_dict.values()) + list(environmentals.values()),
        )

        while self._time < stop:
            self._fmu.doStep(
                currentCommunicationPoint=self._time,
                communicationStepSize=self._step_size,
            )

            self._time += self._step_size

        output_names = self._sensors_cls.model_fields.keys()
        outputs = self._fmu.getReal(self._var_mapper(output_names))
        return self._sensors_cls(**dict(zip(output_names, outputs)))
    
    @property
    def time(self):
        return self._time
