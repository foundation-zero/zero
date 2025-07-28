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
    cooling_mix_setpoint: Annotated[Celsius, Field(le=90)] = 85
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
_INITIAL_CONTROL_VALUES = (
    PvtControlValues(
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
)


class PvtControl(Control):
    def __init__(self, parameters: PvtParameters):
        self._parameters = parameters
        self._states = [
            State(
                name="idle",
                on_enter=[self._deactivate_pumps, self._disable_heat_dump_mix],
                on_exit=[self._activate_pumps, self._enable_heat_dump_mix],
            ),
            State(
                name="recovery",
                on_enter=self._enable_recovery_mixes,
                on_exit=self._disable_recovery_mixes,
            ),
            State(name="pump_failure", on_enter=self._set_recovery_mixes_to_a),
        ]

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
        self.pvt_state_machine = Machine(model=self, states=self._states, initial="idle")
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._time = datetime.now()

    @property
    def parameters(self) -> PvtParameters:
        return self._parameters

    @property
    def modes(self) -> list[str]:
        return list(self.pvt_state_machine.states.keys())

    @property
    def mode(self) -> Literal["idle", "recovery", "pump_failure"]:
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

    def _set_recovery_mixes_to_a(self):
        self._current_values.pvt_mix_main_fwd.setpoint = Stamped(
            value=Valve.MIXING_A_TO_AB,
            timestamp=self._time,
        )
        self._current_values.pvt_mix_main_aft.setpoint = Stamped(
            value=Valve.MIXING_A_TO_AB,
            timestamp=self._time,
        )
        self._current_values.pvt_mix_owners.setpoint = Stamped(
            value=Valve.MIXING_A_TO_AB,
            timestamp=self._time,
        )

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
        # Using the max of the three temperatures to control the heat dump
        # This should limit the output temperature
        # Possibly this is too slow, if there is a sudden drop in heat consumption
        # At that point we should instead predict the output temperature based on the
        # exchanger temperature and the PVT heat flow
        # FIXME: either have the FDS adapted to match this functionality
        # (inclusive) or change the control logic
        self._current_values.pvt_mix_exchanger.setpoint = Stamped(
            value=(
                self._heat_dump_controller(
                    max(
                        sensor_values.pvt_temperature_main_aft_return.temperature.value,
                        sensor_values.pvt_temperature_main_fwd_return.temperature.value,
                        sensor_values.pvt_temperature_owners_return.temperature.value,
                    ),
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
        strings_main_fwd_flow = (
            sensor_values.pvt_flow_main_string_1_1.flow.value  # TODO: fix in simulation
            # + sensor_values.pvt_flow_main_string_1_2.flow.value
            # + sensor_values.pvt_flow_main_string_2_1.flow.value
            # + sensor_values.pvt_flow_main_string_2_2.flow.value
            # + sensor_values.pvt_flow_main_string_3.flow.value
            # + sensor_values.pvt_flow_main_string_4.flow.value
            # + sensor_values.pvt_flow_main_string_5_1.flow.value
            # + sensor_values.pvt_flow_main_string_5_2.flow.value
            # + sensor_values.pvt_flow_main_string_6_1.flow.value
            # + sensor_values.pvt_flow_main_string_6_2.flow.value
        )

        strings_main_aft_flow = (
            sensor_values.pvt_flow_main_string_7_1.flow.value  # TODO: fix in simulation
            # + sensor_values.pvt_flow_main_string_7_2.flow.value
            # + sensor_values.pvt_flow_main_string_8_1.flow.value
            # + sensor_values.pvt_flow_main_string_8_2.flow.value
            # + sensor_values.pvt_flow_main_string_9.flow.value
            # + sensor_values.pvt_flow_main_string_10.flow.value
            # + sensor_values.pvt_flow_main_string_11_1.flow.value
        )

        strings_owners_flow = (
            sensor_values.pvt_flow_owners_string_1.flow.value
            # + sensor_values.pvt_flow_owners_string_2.flow.value
            # + sensor_values.pvt_flow_owners_string_3.flow.value
            # + sensor_values.pvt_flow_owners_string_4.flow.value
            # + sensor_values.pvt_flow_owners_string_5.flow.value
            # + sensor_values.pvt_flow_owners_string_6.flow.value
        )

        self._current_values.pvt_pump_main_fwd.dutypoint = Stamped(
            value=self._main_fwd_pump_flow_controller(
                strings_main_fwd_flow,
                self._time,
            ),
            timestamp=self._time,
        )
        self._current_values.pvt_pump_main_aft.dutypoint = Stamped(
            value=self._main_aft_pump_flow_controller(
                strings_main_aft_flow,
                self._time,
            ),
            timestamp=self._time,
        )
        self._current_values.pvt_pump_owners.dutypoint = Stamped(
            value=self._owners_pump_flow_controller(
                strings_owners_flow,
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
