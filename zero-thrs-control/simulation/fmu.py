from datetime import timedelta
from types import TracebackType
from typing import Any, Callable, Iterable, Self, cast

from fmpy import extract, read_model_description
from fmpy.fmi2 import FMU2Slave
from fmpy.model_description import ModelDescription


def _var_mapper(
    model_description: ModelDescription,
) -> Callable[[Iterable[str]], list[int]]:
    _var_name_to_ref = {
        variable.name: variable.valueReference
        for variable in model_description.modelVariables
    }
    return lambda names: [_var_name_to_ref[name] for name in names]


class Fmu:
    def __init__(
        self,
        file: str,
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
        self._fmu.instantiate()
        self._fmu.setupExperiment(startTime=0.0)
        self._fmu.enterInitializationMode()
        self._fmu.exitInitializationMode()
        self._output_names = [
            var.name
            for var in model_description.modelVariables
            if var.causality == "output"
        ]
        self._initial_outputs = dict(zip(self._output_names, self._fmu.getReal(self._var_mapper(self._output_names))))  # type: ignore

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
        inputs: dict[str, Any],
        duration: timedelta,
    ) -> dict[str, Any]:

        stop = self._time + duration.total_seconds()

        self._fmu.setReal(self._var_mapper(inputs.keys()), list(inputs.values()))

        while self._time < stop:
            self._fmu.doStep(
                currentCommunicationPoint=self._time,
                communicationStepSize=self._step_size,
            )

            self._time += self._step_size

        return cast(dict[str, Any], dict(zip(self._output_names, self._fmu.getReal(self._var_mapper(self._output_names)))))  # type: ignore

    @property
    def solver_time(self):
        return self._time
