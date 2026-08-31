from abc import ABC
from typing import Annotated

from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.system import AmcsControlMode


class AmcsModeSensorValues(ThrsValues, ABC):
    mode: Annotated[AmcsControlMode, component_meta(included_in_fmu=False)]
