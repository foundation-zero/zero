from datetime import datetime
from typing import Callable

from thrs.classes.control import Control
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import ThrsValues


class ModuleDescription[
    S: ThrsValues,
    C: ThrsValues,
    P: ThrsValues,
    M: ThrsValues,
]:
    """Description of a module with sensor values, control values, control parameters and control mode models and the control & alarm logic"""

    def __init__(
        self,
        sensor_values_cls: type[S],
        control_values_cls: type[C],
        parameters_cls: type[P],
        control: Callable[[P, Callable[[], datetime]], Control[S, C, P, M]],
        control_mode_cls: type[M],
        alarms: Callable[[], BaseAlarms[S, C, P]],
    ):
        self.sensor_values_cls = sensor_values_cls
        self.control_values_cls = control_values_cls
        self.parameters_type = parameters_cls
        self.control_mode_cls = control_mode_cls
        self.control = control
        self.alarms = alarms

    @property
    def input_values_type(self) -> ThrsValues:
        return self.sensor_values_cls

    @property
    def output_values_type(self) -> ThrsValues:
        return self.control_values_cls
