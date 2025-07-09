import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import polars as pl


def compute_heat(temp1, temp2, flow):
    return (
        (temp1 - temp2) * flow * 3769 / 60
    )  # 3769 is specific heat capacity of 20% glycol mixture


def strip_names(df):
    return df.rename(
        columns={col: col.split("__")[0].split("_", 1)[-1] for col in df.columns} #removes module name, variable name and unit. So 'thrusters_mix_aft__position_rel__ratio' becomes 'mix_aft'
    )


def plot_frames(frames: list[pd.DataFrame], path: str):
    sns.set_style("whitegrid")
    plt.rcParams["axes.grid"] = True
    plt.rcParams["axes.grid.axis"] = "y"

    fig, axes = plt.subplots(len(frames), 1, figsize=(10, len(frames) * 2), sharex=True)

    for i, df in enumerate(frames):
        sns.lineplot(df, linewidth=2.5, ax=axes[i])
        axes[i].legend(loc="center left", bbox_to_anchor=(1, 0.5))

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    plt.tight_layout()
    plt.savefig(
        path,
        bbox_inches="tight",
        dpi=300,
    )

    return fig, axes


def plot_result(result: pl.DataFrame, path: str):
    valve_keys = [col for col in result.columns if "__position_rel__" in col]
    flow_keys = [
        col for col in result.columns if "__flow__" in col and "string" not in col
    ]
    temperature_keys = [
        col
        for col in result.columns
        if "__temperature__" in col and "string" not in col and "flow" not in col
    ]
    dutypoint_keys = [col for col in result.columns if "__dutypoint__" in col]

    selected_keys = [dutypoint_keys, valve_keys, temperature_keys, flow_keys]
    modules = list(
        set([
            col.split("_")[0]
            for col in result.columns
            if col not in ["time", "control_mode"]
        ])
    )

    result_frames = {
        module: [
            result.select([
                col
                for col in result.columns
                if (col in keys and module in col) or col == "time"
            ])
            .to_pandas()
            .set_index("time")
            for keys in selected_keys
        ]
        for module in modules
    }

    sns.set_style("whitegrid")
    plt.rcParams["axes.grid"] = True
    plt.rcParams["axes.grid.axis"] = "y"

    nrows = len(selected_keys)
    ncols = len(modules)

    fig, axes = plt.subplots(
        nrows, ncols, figsize=(18, nrows * 2.5), sharex=True, sharey="row"
    )

    # Ensure axes are always 2D for consistent indexing
    if nrows == 1 and ncols == 1:
        axes = axes.reshape((1, 1))
    elif nrows == 1:
        axes = axes[np.newaxis, :]
    elif ncols == 1:
        axes = axes[:, np.newaxis]

    # Plot each module's data
    for j, module in enumerate(modules):
        for i in range(len(selected_keys)):
            df = result_frames[module][i]
            df = strip_names(df)
            ax = axes[i, j]
            sns.lineplot(df, linewidth=2.5, ax=ax)
            ax.legend(
                loc="center left",
                bbox_to_anchor=(1.01, 0.5),
                fontsize="small",
                frameon=False,
            )
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    # Shade background by control_mode
    if len(result.select("control_mode").drop_nulls()) > 0:
        control_modes = (
            result.select(["time", "control_mode"])
            .to_pandas()
            .set_index("time")
            .squeeze()
        )
        palette = sns.color_palette("pastel", control_modes.nunique()) # type: ignore
        mode_colors = {
            mode: palette[i] for i, mode in enumerate(control_modes.unique()) # type: ignore
        }
        last_modes = control_modes[control_modes != control_modes.shift(-1)] # type: ignore
        start = control_modes.index[0] # type: ignore
        for end, mode in last_modes.items(): # type: ignore
            for ax in axes.flatten():
                ax.axvspan(start, end, color=mode_colors[mode], alpha=0.2)

            for ax in axes[0, :]:
                ax.annotate(
                    mode,
                    xy=(start + (end - start)/4, 1.02), # type: ignore
                    xycoords=("data", "axes fraction"),
                    ha="center",
                    va="bottom",
                    fontsize="small",
                    color="black",
                    alpha=0.8,
                )
            start = end

    ylabels = [
        "Dutypoint [ratio]",
        "Valve position [ratio]",
        "Temperature [°C]",
        "Flow [l/min]",
    ]
    for idx, label in enumerate(ylabels):
        axes[idx, 0].set_ylabel(label)

    for i, module in enumerate(modules):
        axes[0, i].set_title(module.capitalize())

    plt.tight_layout()
    plt.savefig(
        path,
        bbox_inches="tight",
        dpi=300,
    )

    return fig, axes
