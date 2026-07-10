import logging
import os
import shutil
from base64 import b64encode
from datetime import timedelta
from tempfile import TemporaryDirectory, gettempdir
from types import TracebackType
from typing import Any, Callable, Iterable, Protocol, Self, cast, runtime_checkable

from fmpy import extract, read_model_description
from fmpy.fmi2 import FMU2Slave
from fmpy.model_description import ModelDescription


@runtime_checkable
class FmuLike(Protocol):
    def tick(self, inputs: dict[str, Any], duration: timedelta) -> dict[str, Any]: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool: ...

    @property
    def solver_time(self) -> float: ...


def _var_mapper(
    model_description: ModelDescription,
) -> Callable[[Iterable[str]], list[int]]:
    _var_name_to_ref = {
        variable.name: variable.valueReference
        for variable in model_description.modelVariables
    }
    return lambda names: [_var_name_to_ref[name] for name in names]


logger = logging.getLogger(__name__)


class Fmu:
    def __init__(
        self,
        file: str,
    ):
        self._model_description = read_model_description(file)

        self._extract_fmu_contents(file)

        self._fmu_instance: FMU2Slave | None = None
        self._var_mapper = _var_mapper(self._model_description)
        self._time = 0.0
        self._output_names = [
            var.name
            for var in self._model_description.modelVariables
            if var.causality == "output"
        ]

    def _extract_fmu_contents(self, file):
        file_path = os.path.abspath(file)
        file_key = b64encode(file_path.encode()).decode().replace("=", "")
        cache_root = os.path.join(gettempdir(), "thrs_fmu_cache")
        os.makedirs(cache_root, exist_ok=True)
        self._cached_unzip_dir = os.path.join(cache_root, f"fmu_{file_key}")

        if not os.path.exists(self._cached_unzip_dir) or os.path.getmtime(
            file_path
        ) > os.path.getmtime(self._cached_unzip_dir):
            if os.path.exists(self._cached_unzip_dir):
                shutil.rmtree(self._cached_unzip_dir, ignore_errors=True)

            extract(file_path, self._cached_unzip_dir)

        # Due to test issues, use an instance-local extraction directory to avoid file locking
        # collisions when multiple tests/processes initialize the same FMU.
        self._temp_dir = TemporaryDirectory(
            prefix=f"fmu_instance_{file_key}_",
            ignore_cleanup_errors=True,
        )
        self._temp_unzip_dir = self._temp_dir.name

        # Copy cached extraction into an instance-local directory to keep DLLs isolated.
        shutil.copytree(
            self._cached_unzip_dir,
            self._temp_unzip_dir,
            dirs_exist_ok=True,
        )

    def initialize(self, inputs: dict[str, Any]):
        fmu = FMU2Slave(
            guid=self._model_description.guid,
            unzipDirectory=self._temp_unzip_dir,
            modelIdentifier=self._model_description.coSimulation.modelIdentifier
            if self._model_description.coSimulation
            else None,
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
        if self._fmu_instance:
            self._fmu_instance.terminate()
            self._fmu_instance.freeInstance()
        if value:
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
