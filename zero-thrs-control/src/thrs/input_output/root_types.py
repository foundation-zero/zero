from abc import ABC
from typing import Annotated

from pydantic import Field

from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.system import AmcsExternalAvailable, AmcsModeStatus


class AmcsModeSensorValues(ThrsValues, ABC):
    mode: Annotated[AmcsModeStatus, component_meta(included_in_fmu=False)]


class AmcsHeartbeatControlValues(ThrsValues, ABC):
    external_available: Annotated[
        AmcsExternalAvailable, component_meta(included_in_fmu=False)
    ] = Field(default_factory=AmcsExternalAvailable)
