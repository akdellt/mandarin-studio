import logging
import numpy as np
from pathlib import Path
from typing import NamedTuple
from fastdtw import fastdtw  # type: ignore
from mandarinstudio.analysis import pitch

logger = logging.getLogger(__name__)

class DtwResult(NamedTuple):
    distance: float
    path: list
    ref_pitch: np.ndarray
    user_pitch: np.ndarray

def run_dtw(ref_audio: Path, user_audio: Path) -> DtwResult:
    ref_pitch = pitch.process_audio(ref_audio)
    user_pitch = pitch.process_audio(user_audio)

    if ref_pitch.size == 0 or user_pitch.size == 0:
        logger.warning("Não foi possível detectar voz em um dos áudios.")
        logger.debug(f"Tamanho referência: {ref_pitch.size}, Tamanho usuário: {user_pitch.size}")
        return DtwResult(np.inf, [], ref_pitch, user_pitch)
    
    distance, path = fastdtw(ref_pitch, user_pitch, dist=lambda x, y: abs(x.item() - y.item()))

    logger.debug(f"Formato referência: {ref_pitch.shape}, Formato usuário: {user_pitch.shape}")
    logger.debug(f"Distância DTW: {distance:.2f}")

    return DtwResult(float(distance), path, ref_pitch, user_pitch)