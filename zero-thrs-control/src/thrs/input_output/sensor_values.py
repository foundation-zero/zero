from abc import ABC

from thrs.input_output.base import ThrsValues
from thrs.input_output.definitions.system import AmcsControlMode


class AmcsModeSensorValues(ThrsValues, ABC):
    @property
    def mode(self) -> AmcsControlMode: ...
