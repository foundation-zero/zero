from datetime import timedelta
import shutil
from types import TracebackType
from typing import Any, Self
from fmpy import extract, read_model_description, instantiate_fmu, simulate_fmu
from fmpy.simulation import apply_start_values


class Fmu:
    def __init__(
        self,
        file: str,
    ):
        self._temp_unzip_dir = extract(file)
        self._model_description = read_model_description(self._temp_unzip_dir)

        self._fmu_instance = instantiate_fmu(
            unzipdir=self._temp_unzip_dir, model_description=self._model_description
        )
        self._time = 0
        self._stabilize()

    def _stabilize(self):
        simulate_fmu(
            filename=self._temp_unzip_dir,
            model_description=self._model_description,
            start_time=self._time,
            stop_time=self._time + 1,
            set_stop_time=False,
            terminate=False,
            output_interval=1,
            initialize=True,
            fmu_instance=self._fmu_instance,
            step_size=0.001,
        )

        self._time = 1

    def tick(
        self,
        inputs: dict[str, Any],
        duration: timedelta,
    ) -> dict[str, Any]:
        apply_start_values(
            fmu=self._fmu_instance,
            model_description=self._model_description,
            start_values=inputs,
        )

        result = simulate_fmu(
            filename=self._temp_unzip_dir,
            model_description=self._model_description,
            start_time=self._time,
            stop_time=self._time + duration.total_seconds(),
            set_stop_time=False,
            terminate=False,
            output_interval=duration.total_seconds(),
            initialize=False,
            fmu_instance=self._fmu_instance,
            step_size=0.001,
        )

        self._time += duration.total_seconds()

        return {
            name: result[-1][name].item()
            for name in result.dtype.names
            if name != "time"
        }

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ):
        self._fmu_instance.terminate()
        self._fmu_instance.freeInstance()
        shutil.rmtree(self._temp_unzip_dir)
        if value is not None:
            raise value
        return True

    @property
    def solver_time(self):
        return self._time
