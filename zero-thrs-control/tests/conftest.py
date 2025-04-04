from pytest import fixture

from control.modules.thrusters import ThrustersControl, ThrustersParameters


@fixture
def thrusters_control() -> ThrustersControl:
    return ThrustersControl(
        ThrustersParameters(
            cooling_mix_setpoint=40,
            recovery_thruster_flow=10,  # 50-S001 50-S002 per thruster
            cooling_thruster_flow=22,  # 50-S012 50-S013 per thruster
            max_temp=80,
            recovery_mix_setpoint=60,
        )
    )
