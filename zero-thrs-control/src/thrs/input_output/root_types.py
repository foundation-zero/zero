from abc import ABC
from typing import Annotated

from pydantic import Field

from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.system import AmcsControlMode, AmcsExternalAvailable


class AmcsModeSensorValues(ThrsValues, ABC):
    mode: Annotated[AmcsControlMode, component_meta(included_in_fmu=False)]


class AmcsWatchdogControlValues(ThrsValues, ABC):
    external_available: Annotated[
        AmcsExternalAvailable, component_meta(included_in_fmu=False)
    ] = Field(default_factory=AmcsExternalAvailable)
