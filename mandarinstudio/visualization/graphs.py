import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from matplotlib.figure import Figure

BACKGROUND_COLOR = "#211A2B"
PLOT_COLOR = "#2D2340"
TEXT_COLOR = "#FFF8E7"
REFERENCE_COLOR = "#BBA3FF"
PRONUNCIATION_COLOR = "#FFE8FF"
GRID_COLOR = "#6E5A8A"


def plot_graph(
    ref_audio: np.ndarray,
    user_audio: np.ndarray,
    path: list,
    distance: float,
    save_path: Path | None = None,
) -> Figure:
    fig, ax = plt.subplots(figsize=(12, 6), facecolor=BACKGROUND_COLOR)
    ax.set_facecolor(PLOT_COLOR)

    ref_aligned = [ref_audio[i] for i, _ in path]
    user_aligned = [user_audio[j] for _, j in path]

    ax.plot(
        ref_aligned,
        label="Áudio de referência",
        color=REFERENCE_COLOR,
        linewidth=3,
    )
    ax.plot(
        user_aligned,
        label="Sua pronúncia",
        color=PRONUNCIATION_COLOR,
        linewidth=3,
        linestyle="--",
    )

    ax.set_ylim(-2.5, 2.5)

    ax.set_title(
        f"Comparação do tom (diferença: {distance:.2f})",
        color=TEXT_COLOR,
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel("Tempo da fala", color=TEXT_COLOR, fontsize=11)
    ax.set_ylabel("Altura do tom", color=TEXT_COLOR, fontsize=11)
    ax.tick_params(colors=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.legend(facecolor=PLOT_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    ax.grid(True, color=GRID_COLOR, alpha=0.45)

    if save_path is not None:
        fig.savefig(save_path, bbox_inches="tight")

    plt.close(fig)
    return fig