import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def plot_graph(
    ref_audio: np.ndarray,
    user_audio: np.ndarray,
    path: list,
    distance: float,
    save_path: Path | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))

    ref_aligned = [ref_audio[i] for i, _ in path]
    user_aligned = [user_audio[j] for _, j in path]

    ax.plot(ref_aligned, label="Reference", color="blue", linewidth=2)
    ax.plot(user_aligned, label="Pronunciation", color="red", linestyle="--", alpha=0.8)

    ax.set_ylim(-2.5, 2.5)

    ax.set_title(f"Aligned Pitch Comparison (DTW Distance: {distance:.2f})")
    ax.set_xlabel("Relative Time (Aligned Frames)")
    ax.set_ylabel("Normalized Frequency (Z-Score)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    if save_path is not None:
        fig.savefig(save_path, bbox_inches="tight")
    else:
        plt.show()

    plt.close(fig)