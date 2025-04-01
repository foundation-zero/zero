import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt


def compute_heat(temp1, temp2, flow):
    return (
        (temp1 - temp2) * flow * 4184 / 60
    )  # TODO: check exact specific heat capacity of medium


def plot_frames(frames: list[pd.DataFrame], path: str):
    fig, axes = plt.subplots(len(frames), 1, figsize=(10, 8), sharex=True)

    for i, df in enumerate(frames):
        sns.lineplot(df, linewidth=2.5, ax=axes[i])
        axes[i].legend(loc="center left", bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    plt.savefig(
        path,
        bbox_inches="tight",
        dpi=300,
    )

    return fig, axes

