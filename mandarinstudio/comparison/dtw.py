import logging
import numpy as np

from pathlib import Path
from typing import NamedTuple
from fastdtw import fastdtw  # type: ignore

from mandarinstudio.analysis import pitch

logger = logging.getLogger(__name__)

class DtwResult(NamedTuple):
    avg_distance: float
    path: list[tuple[int, int]]
    ref_pitch: np.ndarray
    user_pitch: np.ndarray

def run_dtw(ref_audio: Path, user_audio: Path) -> DtwResult:
    ref_pitch = pitch.process_audio(ref_audio)
    user_pitch = pitch.process_audio(user_audio)

    # Returns infinite distance if either audio lacks voiced segments (silence/whisper)
    if ref_pitch.size == 0 or user_pitch.size == 0:
        logger.warning("It was not possible to detect a voice in one of the audio files.")
        logger.debug(f"Reference size: {ref_pitch.size}, User size: {user_pitch.size}")
        return DtwResult(np.inf, [], ref_pitch, user_pitch)

    # Custom 1D distance: extracts scalar values from (1,) arrays to compute absolute pitch difference
    distance, path = fastdtw(ref_pitch, user_pitch, dist=lambda x, y: abs(x.item() - y.item()))
    avg_distance = (distance / len(path)) if path else np.inf

    logger.debug(f"Reference format: {ref_pitch.shape}, User Format: {user_pitch.shape}")
    logger.debug(f"DTW average distance: {avg_distance:.2f}")

    return DtwResult(float(avg_distance), path, ref_pitch, user_pitch)