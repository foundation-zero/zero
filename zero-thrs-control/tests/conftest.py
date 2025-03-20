from pytest import fixture

from control.modules.thrusters import ThrustersControl, ThrustersParameters


@fixture
def thrusters_control() -> ThrustersControl:
    return ThrustersControl(ThrustersParameters(cooling_mix_setpoint=40, cooling_pump_dutypoint=0.9, recovery_pump_dutypoint=0.5, max_temp=70, recovery_mix_setpoint=60))
