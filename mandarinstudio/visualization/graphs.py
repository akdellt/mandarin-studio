import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def plot_graph(
    ref_audio: np.ndarray, user_audio: np.ndarray,
    path: list, distance: float,
    save_path: Path | None = None,
) -> None:
    plt.figure(figsize=(12, 6))

    ref_aligned = []
    user_aligned = []

    for i, j in path:
        ref_aligned.append(ref_audio[i])
        user_aligned.append(user_audio[j])

    plt.plot(ref_aligned, label="Referência", color='blue', linewidth=2)
    plt.plot(user_aligned, label="Pronúncia", color='red', linestyle='--', alpha=0.8)

    plt.title(f"Comparação de Pitch Alinhada (DTW Distance: {distance:.2f})")
    plt.xlabel("Tempo Relativo (Frames Alinhados)")
    plt.ylabel("Frequência Normalizada (Z-Score)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    if save_path is not None:
        plt.savefig(save_path)
    else:
        plt.show()