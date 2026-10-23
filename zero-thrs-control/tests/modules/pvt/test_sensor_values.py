from datetime import timedelta

from pytest import approx

from tests.modules.pvt.conftest import PvtRunner
from thrs.control.modules.pvt import PvtControl
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import HeatSource
from thrs.input_output.modules.pvt import PvtSimulationInputs


def test_main_heat_combines_aft_and_fwd(
    runner: PvtRunner,
    control: PvtControl,
    simulation_inputs: PvtSimulationInputs,
):
    runner.update_simulation_inputs(
        simulation_inputs.model_copy(
            update={
                "pvt_main_aft": HeatSource(heat_flow=Stamped.stamp(8000)),
                "pvt_main_fwd": HeatSource(heat_flow=Stamped.stamp(16000)),
            }
        )
    )

    sensor_values, *_ = runner.run_until(
        lambda *_: control.mode.aft.mode != "idle" and control.mode.fwd.mode != "idle",
        within=timedelta(minutes=10),
    )
    sensor_values, *_ = runner.tick()

    aft = sensor_values.pvt_pvt_main_aft_heat
    fwd = sensor_values.pvt_pvt_main_fwd_heat
    main = sensor_values.pvt_pvt_main_heat

    assert aft.flow.value is not None and fwd.flow.value is not None
    assert aft.heat.value is not None and fwd.heat.value is not None
    assert aft.flow.value > 0 and fwd.flow.value > 0
    assert main.flow.value == approx(aft.flow.value + fwd.flow.value)
    assert main.heat.value == approx(aft.heat.value + fwd.heat.value)

    for field in ("temperature_supply", "temperature_return"):
        lower, upper = sorted(
            [getattr(aft, field).value, getattr(fwd, field).value],
        )
        assert lower <= getattr(main, field).value <= upper
