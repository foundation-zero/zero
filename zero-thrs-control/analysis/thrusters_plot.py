import asyncio
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from control.modules.thrusters import ThrustersControl, ThrustersParameters
from input_output.base import Stamped, StampedDf
from input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    TemperatureBoundary,
)
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from orchestration.simulator import Simulator, SimulatorModel
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt


# simulate scenario: start in recovery, increase thrusters source (trigger warm-up mixing), increase input temp (trigger cooling mode)
start_time = datetime.fromtimestamp(0)
duration = timedelta(minutes=59)

supply_temperature = StampedDf.stamp(
    pl.DataFrame({
        "time": pl.datetime_range(
            start_time, start_time + duration, interval="1m", time_unit="us", eager=True
        ),
        "value": 30 * [50.0] + 30 * [80.0],
    })
)

simulation_inputs = ThrustersSimulationInputs(
    thrusters_aft=HeatSource(heat_flow=Stamped.stamp(9000.0)),
    thrusters_fwd=HeatSource(heat_flow=Stamped.stamp(4300.0)),
    thrusters_seawater_supply=Boundary(
        temperature=Stamped.stamp(32.0), flow=Stamped.stamp(64.0)
    ),
    thrusters_module_supply=TemperatureBoundary(temperature=supply_temperature),
)

control = ThrustersControl(
    ThrustersParameters(
        cooling_mix_setpoint=40,
        cooling_pump_dutypoint=0.9,
        recovery_pump_dutypoint=0.5,
        max_temp=70,
        recovery_mix_setpoint=60,
    )
)
control.to_recovery() # type: ignore

thrusters_model = SimulatorModel(
    fmu_path=str( Path(__file__).resolve().parent.parent / "src/simulation/models/thrusters/thruster_moduleV6.fmu"),
    sensor_values_cls=ThrustersSensorValues,
    control_values_cls=ThrustersControlValues,
    simulation_outputs_cls=ThrustersSimulationOutputs,
    simulation_inputs=simulation_inputs,
    control=control,
    tick_duration=timedelta(seconds=10),
    start_time=start_time,
)

simulation = Simulator(thrusters_model)


result = asyncio.run(simulation.run(6 * 60))

df = result.group_by_dynamic("time", every="1m").agg([  # type: ignore
    pl.col("*").mean()
])


def compute_heat(temp1, temp2, flow):
    return (
        (temp1 - temp2) * flow * 4184 / 60
    )  # TODO: check exact specific heat capacity of medium


heat = pl.DataFrame({
    "thrusters_heat_recovered": compute_heat(
        df["thrusters_module_return__temperature__C"],
        df["thrusters_module_supply__temperature__C"],
        df["thrusters_module_supply__flow__l_min"],
    ),
    "thrusters_heat_dumped": compute_heat(
        df["thrusters_seawater_return__temperature__C"],
        df["thrusters_seawater_supply__temperature__C"],
        df["thrusters_seawater_supply__flow__l_min"],
    ),
    "thrusters_aft_heat": compute_heat(
        df["thrusters_temperature_aft_return__temperature__C"],
        df["thrusters_temperature_aft_supply__temperature__C"],
        df["thrusters_flow_aft__flow__l_min"],
    ),
    "thrusters_fwd_heat": compute_heat(
        df["thrusters_temperature_fwd_return__temperature__C"],
        df["thrusters_temperature_fwd_supply__temperature__C"],
        df["thrusters_flow_fwd__flow__l_min"],
    ),
})

heat_df = heat.with_columns(df["time"]).to_pandas().set_index("time")
temp_df = (
    df.select([col for col in df.columns if "__temperature__" in col or col == "time"])
    .to_pandas()
    .set_index("time")
)
flow_df = (
    df.select([col for col in df.columns if "__flow__" in col or col == "time"])
    .to_pandas()
    .set_index("time")
)
valve_df = (
    df.select([
        col
        for col in df.columns
        if ("__position_rel__" in col and "mix" in col) or col == "time"
    ])
    .to_pandas()
    .set_index("time")
)


frames = [heat_df, temp_df, flow_df, valve_df]


def plot_frames(frames: list[pd.DataFrame]):
    fig, axes = plt.subplots(len(frames), 1, figsize=(10, 8), sharex=True)

    for i, df in enumerate(frames):
        sns.lineplot(df, linewidth=2.5, ax=axes[i])
        axes[i].legend(loc="center left", bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    plt.savefig(
        "analysis/thrusters_plot.png",
        bbox_inches="tight",
        dpi=300,
    )

    return fig, axes


plot_frames(frames)
