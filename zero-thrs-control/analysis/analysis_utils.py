import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def compute_heat(temp1, temp2, flow):
    return (
        (temp1 - temp2) * flow * 4184 / 60
    )  # TODO: check exact specific heat capacity of medium


def plot_frames(frames: list[pd.DataFrame], path: str):
    sns.set_style("whitegrid")
    plt.rcParams["axes.grid"] = True
    plt.rcParams["axes.grid.axis"] = "y"

    fig, axes = plt.subplots(len(frames), 1, figsize=(10, len(frames)*2), sharex=True)

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

