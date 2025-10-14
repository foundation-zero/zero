from datetime import datetime
from typing import Annotated, Callable, Literal
from pydantic import Field, model_validator

from thrs.classes.control import Control, ControlResult
from thrs.control.controllers import Controller
from thrs.control.modules.pvt_group import PvtGroupControl, PvtGroupParameters
from thrs.input_output.base import Stamped, ThrsModel
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import Celsius, Ratio, Tuning
from thrs.input_output.modules.pvt import PvtControlValues, PvtSensorValues
from thrs.input_output.modules.pvt_group import PvtGroupSensorValues


class PvtParameters(ThrsModel):
    maximum_supply_temperature: Annotated[Celsius, Field(le=90)] = 80
    recovery_temperature: Celsius = 70
    warmup_temperature: Celsius = 55
    recovery_activation_string_temperature: Celsius = 40
    minimum_return_temperature: Celsius = 40
    main_fwd_minimum_pump_dutypoint: Ratio = 0.2  # minimum dutpypoint to ensure flow past temperature sensor in recovery mode
    main_aft_minimum_pump_dutypoint: Ratio = 0.2  # minimum dutpypoint to ensure flow past temperature sensor in recovery mode
    owners_minimum_pump_dutypoint: Ratio = 0.2  # minimum dutpypoint to ensure flow past temperature sensor in recovery mode
    heat_dump_tuning: Tuning = (0.05, 0.001, 0.0)
    main_fwd_mix_tuning: Tuning = (-0.005, -0.001, 0.0)
    main_aft_mix_tuning: Tuning = (-0.005, -0.001, 0.0)
    owners_mix_tuning: Tuning = (-0.005, -0.001, 0.0)
    main_fwd_pump_tuning: Tuning = (
        -0.001,
        -0.0005,
        0.0,
    )  # 0.022 approximate ultimate gain (max Kp with sustained oscillations)
    main_aft_pump_tuning: Tuning = (
        -0.001,
        -0.0005,
        -0.0,
    )  # 0.22 approximate ultimate gain (max Kp with sustained oscillations)
    owners_pump_tuning: Tuning = (
        -0.001,
        -0.0005,
        -0.0,
    )  # 0.042 approximate ultimate gain (max Kp with sustained oscillations)

    @model_validator(mode="after")
    def check_temperature_setpoints(self):
        if self.recovery_temperature < self.warmup_temperature:
            raise ValueError(
                "Recovery temperature must be greater than warmup temperature"
            )
        if self.warmup_temperature < self.minimum_return_temperature:
            raise ValueError(
                "Warmup temperature must be greater than minimum return temperature"
            )
        return self


_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = PvtControlValues(
    pvt_pump_main_fwd=Pump(
        dutypoint=Stamped(value=0.0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    pvt_pump_main_aft=Pump(
        dutypoint=Stamped(value=0.0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    pvt_pump_owners=Pump(
        dutypoint=Stamped(value=0.0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    pvt_mix_main_fwd=Valve(
        setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=_ZERO_TIME)
    ),
    pvt_mix_main_aft=Valve(
        setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=_ZERO_TIME)
    ),
    pvt_mix_owners=Valve(
        setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=_ZERO_TIME)
    ),
    pvt_switch_main_fwd=Valve(setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)),
    pvt_switch_main_aft=Valve(setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)),
    pvt_switch_owners=Valve(setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)),
    pvt_mix_exchanger=Valve(
        setpoint=Stamped(
            value=Valve.MIXING_A_TO_AB,
            timestamp=_ZERO_TIME,
        )
    ),
)


class PvtControl(Control[PvtSensorValues, PvtControlValues, PvtParameters]):
    def __init__(
        self, parameters: PvtParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)

        self._heat_dump_controller = Controller[Ratio, Celsius](
            _INITIAL_CONTROL_VALUES.pvt_mix_exchanger.setpoint.value,
            parameters.maximum_supply_temperature,
            parameters.heat_dump_tuning,
            self._time,
        )

        self._heat_dump_controller.enable()  # always enabled

        self._main_fwd_control = PvtGroupControl(
            PvtGroupParameters(
                warmup_temperature=parameters.warmup_temperature,
                recovery_temperature=parameters.recovery_temperature,
                warmup_mix_tuning=parameters.main_fwd_mix_tuning,
                pump_tuning=parameters.main_fwd_pump_tuning,
                minimum_pump_dutypoint=parameters.main_fwd_minimum_pump_dutypoint,
                recovery_activation_string_temperature=parameters.recovery_activation_string_temperature,
                minimum_return_temperature=parameters.minimum_return_temperature,
            ),
            time_fn,
        )
        self._main_aft_control = PvtGroupControl(
            PvtGroupParameters(
                warmup_temperature=parameters.warmup_temperature,
                recovery_temperature=parameters.recovery_temperature,
                warmup_mix_tuning=parameters.main_aft_mix_tuning,
                pump_tuning=parameters.main_aft_pump_tuning,
                minimum_pump_dutypoint=parameters.main_aft_minimum_pump_dutypoint,
                recovery_activation_string_temperature=parameters.recovery_activation_string_temperature,
                minimum_return_temperature=parameters.minimum_return_temperature,
            ),
            time_fn,
        )
        self._owners_control = PvtGroupControl(
            PvtGroupParameters(
                warmup_temperature=parameters.warmup_temperature,
                recovery_temperature=parameters.recovery_temperature,
                warmup_mix_tuning=parameters.owners_mix_tuning,
                pump_tuning=parameters.owners_pump_tuning,
                minimum_pump_dutypoint=parameters.owners_minimum_pump_dutypoint,
                recovery_activation_string_temperature=parameters.recovery_activation_string_temperature,
                minimum_return_temperature=parameters.minimum_return_temperature,
            ),
            time_fn,
        )

    @property
    def parameters(self) -> PvtParameters:
        return self._parameters

    @property
    def mode(self) -> Literal[""]:
        return ""

    @staticmethod
    def modes() -> list[str]:
        return [""]

    @staticmethod
    def initial_mode() -> str:
        return ""

    def initial(self) -> ControlResult[PvtControlValues]:
        return ControlResult(self._time(), self._current_values)

    def _enable_heat_dump_mix(self):
        self._heat_dump_controller.enable()

    def _disable_heat_dump_mix(self):
        self._heat_dump_controller.disable()

    def _control_heat_dump_mix(self, sensor_values: PvtSensorValues):
        self._current_values.pvt_mix_exchanger.setpoint = Stamped(
            value=self._heat_dump_controller(
                sensor_values.pvt_temperature_supply.temperature.value
            ),
            timestamp=self._time(),
        )

    def _control_groups(self, sensor_values: PvtSensorValues):
        main_fwd_sensor_values = PvtGroupSensorValues(
            pump=sensor_values.pvt_pump_main_fwd,
            temperature_supply=sensor_values.pvt_temperature_main_fwd_supply,
            temperature_return=sensor_values.pvt_temperature_main_fwd_return,
            pressure=sensor_values.pvt_pressure_main_fwd,
            mix=sensor_values.pvt_mix_main_fwd,
            max_temperature_strings=sensor_values.pvt_max_temperature_main_fwd_strings,
        )
        main_aft_sensor_values = PvtGroupSensorValues(
            pump=sensor_values.pvt_pump_main_aft,
            temperature_supply=sensor_values.pvt_temperature_main_aft_supply,
            temperature_return=sensor_values.pvt_temperature_main_aft_return,
            pressure=sensor_values.pvt_pressure_main_aft,
            mix=sensor_values.pvt_mix_main_aft,
            max_temperature_strings=sensor_values.pvt_max_temperature_main_aft_strings,
        )
        owners_sensor_values = PvtGroupSensorValues(
            pump=sensor_values.pvt_pump_owners,
            temperature_supply=sensor_values.pvt_temperature_owners_supply,
            temperature_return=sensor_values.pvt_temperature_owners_return,
            pressure=sensor_values.pvt_pressure_owners,
            mix=sensor_values.pvt_mix_owners,
            max_temperature_strings=sensor_values.pvt_max_temperature_owners_strings,
        )

        self._main_fwd_control.control(main_fwd_sensor_values)
        self._main_aft_control.control(main_aft_sensor_values)
        self._owners_control.control(owners_sensor_values)

    def control(
        self, sensor_values: PvtSensorValues
    ) -> ControlResult[PvtControlValues]:
        self._control_heat_dump_mix(sensor_values)

        self._control_groups(sensor_values)

        self._current_values.pvt_pump_main_fwd = (
            self._main_fwd_control.current_values.pump
        )
        self._current_values.pvt_pump_main_aft = (
            self._main_aft_control.current_values.pump
        )
        self._current_values.pvt_pump_owners = self._owners_control.current_values.pump
        self._current_values.pvt_mix_main_fwd = (
            self._main_fwd_control.current_values.mix
        )
        self._current_values.pvt_mix_main_aft = (
            self._main_aft_control.current_values.mix
        )
        self._current_values.pvt_mix_owners = self._owners_control.current_values.mix

        return ControlResult(self._time(), self._current_values)
