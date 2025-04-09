from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from transitions import Machine, State

from classes.control import Control, ControlResult
from control.controllers import (
    HeatSupplyController,
    InvertedHeatDumpController,
    PumpFlowController,
)
from input_output.base import ParameterMeta, Stamped
from input_output.definitions.control import Pump, Valve
from input_output.definitions.units import Celsius, LMin
from input_output.modules.pvt import PvtControlValues, PvtSensorValues


class PvtParameters(BaseModel):
    cooling_mix_setpoint: Annotated[Celsius, Field(le=90), ParameterMeta("50-S027")] = (
        90
    )
    main_fwd_mix_setpoint: Annotated[
        Celsius, Field(ge=40, le=90), ParameterMeta("50-S019")
    ] = 65
    main_aft_mix_setpoint: Annotated[
        Celsius, Field(ge=40, le=90), ParameterMeta("50-S019")
    ] = 65
    owners_mix_setpoint: Annotated[
        Celsius, Field(ge=40, le=90), ParameterMeta("50-S019")
    ] = 65
    main_fwd_flow_setpoint: Annotated[LMin, Field(le=38), ParameterMeta("50-S020")] = (
        30  # TODO: add minimum based of FDS
    )
    main_aft_flow_setpoint: Annotated[LMin, Field(le=38), ParameterMeta("50-S023")] = (
        30  # TODO: add minimum based of FDS
    )
    owners_flow_setpoint: Annotated[LMin, Field(le=23), ParameterMeta("50-S020")] = (
        15  # TODO: add minimum based of FDS
    )


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
        setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=_ZERO_TIME)
    ),
    pvt_mix_main_aft=Valve(
        setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=_ZERO_TIME)
    ),
    pvt_mix_owners=Valve(
        setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=_ZERO_TIME)
    ),
    pvt_flowcontrol_main_fwd=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pvt_flowcontrol_main_aft=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pvt_flowcontrol_owners=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pvt_mix_exchanger=Valve(
        setpoint=Stamped(
            value=Valve.MIXING_A_TO_AB,
            timestamp=_ZERO_TIME,
        )
    ),
)

states = [
    State(
        name="idle",
        on_enter=["_deactivate_pumps", "_disable_heat_dump_mix"],
        on_exit=["_activate_pumps", "_enable_heat_dump_mix"],
    ),
    State(
        name="recovery",
        on_enter="_enable_recovery_mixes",
        on_exit="_disable_recovery_mixes",
    ),
]


class PvtControl(Control):
    def __init__(self, parameters: PvtParameters):
        self._parameters = parameters
        self._heat_dump_controller = InvertedHeatDumpController(
            _INITIAL_CONTROL_VALUES.pvt_mix_exchanger.setpoint.value,
            parameters.cooling_mix_setpoint,
        )
        self._main_fwd_heat_supply_controller = HeatSupplyController(
            _INITIAL_CONTROL_VALUES.pvt_mix_main_fwd.setpoint.value,
            parameters.main_fwd_mix_setpoint,
        )
        self._main_aft_heat_supply_controller = HeatSupplyController(
            _INITIAL_CONTROL_VALUES.pvt_mix_main_aft.setpoint.value,
            parameters.main_aft_mix_setpoint,
        )
        self._owners_heat_supply_controller = HeatSupplyController(
            _INITIAL_CONTROL_VALUES.pvt_mix_owners.setpoint.value,
            parameters.owners_mix_setpoint,
        )
        self._main_fwd_pump_flow_controller = PumpFlowController(
            _INITIAL_CONTROL_VALUES.pvt_pump_main_fwd.dutypoint.value, 0
        )
        self._main_aft_pump_flow_controller = PumpFlowController(
            _INITIAL_CONTROL_VALUES.pvt_pump_main_aft.dutypoint.value, 0
        )
        self._owners_pump_flow_controller = PumpFlowController(
            _INITIAL_CONTROL_VALUES.pvt_pump_owners.dutypoint.value, 0
        )
        self.machine = Machine(model=self, states=states, initial="idle")
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._time = datetime.now()

    @property
    def mode(self) -> Literal["idle", "recovery"]:
        return self.state  # type: ignore

    def initial(self, time: datetime) -> ControlResult[PvtControlValues]:
        return ControlResult(time, self._current_values)

    def _enable_recovery_mixes(self):
        self._main_fwd_heat_supply_controller.enable()
        self._main_aft_heat_supply_controller.enable()
        self._owners_heat_supply_controller.enable()

    def _disable_recovery_mixes(self):
        self._main_fwd_heat_supply_controller.disable()
        self._main_aft_heat_supply_controller.disable()
        self._owners_heat_supply_controller.disable()

    def _enable_heat_dump_mix(self):
        self._heat_dump_controller.enable()

    def _disable_heat_dump_mix(self):
        self._heat_dump_controller.disable()

    def _control_recovery_mixes(self, sensor_values: PvtSensorValues):
        self._current_values.pvt_mix_main_fwd.setpoint = Stamped(
            value=(
                self._main_fwd_heat_supply_controller(
                    sensor_values.pvt_temperature_main_fwd_return.temperature.value,
                    self._time,
                )
            ),
            timestamp=self._time,
        )
        self._current_values.pvt_mix_main_aft.setpoint = Stamped(
            value=(
                self._main_aft_heat_supply_controller(
                    sensor_values.pvt_temperature_main_aft_return.temperature.value,
                    self._time,
                )
            ),
            timestamp=self._time,
        )
        self._current_values.pvt_mix_owners.setpoint = Stamped(
            value=(
                self._owners_heat_supply_controller(
                    sensor_values.pvt_temperature_owners_return.temperature.value,
                    self._time,
                )
            ),
            timestamp=self._time,
        )

    def _control_heat_dump_mix(self, sensor_values: PvtSensorValues):
        self._current_values.pvt_mix_exchanger.setpoint = Stamped(
            value=(
                self._heat_dump_controller(
                    sensor_values.pvt_temperature_exchanger.temperature.value,
                    self._time,
                )
            ),
            timestamp=self._time,
        )

    def control(
        self, sensor_values: PvtSensorValues, time: datetime
    ) -> ControlResult[PvtControlValues]:
        self._time = time

        self._control_recovery_mixes(sensor_values)
        self._control_heat_dump_mix(sensor_values)

        self._control_pumps(sensor_values)

        return ControlResult(time, self._current_values)

    def _control_pumps(self, sensor_values: PvtSensorValues):
        self._current_values.pvt_pump_main_fwd.dutypoint = Stamped(
            value=self._main_fwd_pump_flow_controller(
                sensor_values.pvt_flow_main_fwd.flow.value,
                self._time,
            ),
            timestamp=self._time,
        )
        self._current_values.pvt_pump_main_aft.dutypoint = Stamped(
            value=self._main_aft_pump_flow_controller(
                sensor_values.pvt_flow_main_aft.flow.value,
                self._time,
            ),
            timestamp=self._time,
        )
        self._current_values.pvt_pump_owners.dutypoint = Stamped(
            value=self._owners_pump_flow_controller(
                sensor_values.pvt_flow_owners.flow.value,
                self._time,
            ),
            timestamp=self._time,
        )

    def _activate_pumps(self):
        self._current_values.pvt_pump_main_fwd.on = Stamped(
            value=True, timestamp=self._time
        )
        self._current_values.pvt_pump_main_aft.on = Stamped(
            value=True, timestamp=self._time
        )
        self._current_values.pvt_pump_owners.on = Stamped(
            value=True, timestamp=self._time
        )

        self._main_fwd_pump_flow_controller.setpoint = (
            self._parameters.main_fwd_flow_setpoint
        )
        self._main_aft_pump_flow_controller.setpoint = (
            self._parameters.main_aft_flow_setpoint
        )
        self._owners_pump_flow_controller.setpoint = (
            self._parameters.owners_flow_setpoint
        )

        self._main_fwd_pump_flow_controller.enable()
        self._main_aft_pump_flow_controller.enable()
        self._owners_pump_flow_controller.enable()

    def _deactivate_pumps(self):
        self._current_values.pvt_pump_main_fwd.on = Stamped(
            value=False, timestamp=self._time
        )
        self._current_values.pvt_pump_main_aft.on = Stamped(
            value=False, timestamp=self._time
        )
        self._current_values.pvt_pump_owners.on = Stamped(
            value=False, timestamp=self._time
        )
        self._main_fwd_pump_flow_controller.disable()
        self._main_aft_pump_flow_controller.disable()
        self._owners_pump_flow_controller.disable()
