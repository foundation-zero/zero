from datetime import timedelta
from types import TracebackType
from typing import Any, Callable, Iterable, Self, cast
from fmpy import extract, read_model_description
from fmpy.model_description import ModelDescription
from fmpy.fmi2 import FMU2Slave


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
    ):
        self._model_description = read_model_description(file)
        self._temp_unzip_dir = extract(file)
        self._fmu_instance: FMU2Slave | None = None
        self._var_mapper = _var_mapper(self._model_description)
        self._time = 0.0
        self._output_names = [
            var.name
            for var in self._model_description.modelVariables
            if var.causality == "output"
        ]

    def initialize(self, inputs: dict[str, Any]):
        fmu = FMU2Slave(
            guid=self._model_description.guid,
            unzipDirectory=self._temp_unzip_dir,
            modelIdentifier=self._model_description.coSimulation.modelIdentifier,
        )
        fmu.instantiate()
        fmu.setupExperiment(tolerance=1e-6, startTime=0.0)
        fmu.enterInitializationMode()
        fmu.setReal(self._var_mapper(inputs.keys()), list(inputs.values()))
        fmu.exitInitializationMode()
        return fmu

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if self._fmu_instance is not None:
            self._fmu_instance.terminate()
            self._fmu_instance.freeInstance()
        if value is not None:
            raise value
        return True

    def tick(
        self,
        inputs: dict[str, Any],
        duration: timedelta,
    ) -> dict[str, Any]:
        if self._fmu_instance is None:
            self._fmu_instance = self.initialize(inputs)
        else:
            self._fmu_instance.setReal(
                self._var_mapper(inputs.keys()), list(inputs.values())
            )

        self._fmu_instance.doStep(
            currentCommunicationPoint=self._time,
            communicationStepSize=duration.total_seconds(),
        )

        self._time += duration.total_seconds()

        return cast(
            dict[str, Any],
            dict(
                zip(
                    self._output_names,
                    self._fmu_instance.getReal(self._var_mapper(self._output_names)),
                )
            ),
        )  # type: ignore

    @property
    def solver_time(self):
        return self._time
