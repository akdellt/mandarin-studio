import numpy as np
import parselmouth

from pathlib import Path
from scipy.signal import savgol_filter

def _extract_pitch_data(audio_path: Path) -> parselmouth.Pitch:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if not audio_path.is_file():
        raise ValueError(f"Path is not a file: {audio_path}")

    try:
        audio = parselmouth.Sound(str(audio_path))
        # Praat defaults (75-600 Hz): broad fundamental frequency (F0) range
        # that safely captures both low male and high female voices.
        pitch = audio.to_pitch(pitch_floor=75, pitch_ceiling=600)
        return pitch
    except parselmouth.PraatError as err:
        raise ValueError(f"Fail to process audio with Praat/Parselmouth: {err}")

# Apply a Savitzky-Golay filter to smooth data preserving the features of original signal
def _smooth_curve(frequencies: np.ndarray, window_length: int=11, polyorder: int=3) -> np.ndarray:
    if len(frequencies) <= window_length:
        return frequencies
    return savgol_filter(frequencies, window_length=window_length, polyorder=polyorder) # type: ignore[return-value]


def _get_clean_frequencies(pitch_object: parselmouth.Pitch, window_length: int=11) -> np.ndarray:
    frequencies_raw = pitch_object.selected_array['frequency']
    # Removes silent frequency points (0.0 or NaN), keeping only actual voice
    frequencies_clean = frequencies_raw[(frequencies_raw > 0) & (~np.isnan(frequencies_raw))]

    # Edge trimming: removes consonant-vowel transition noise and TTS fade-out artifacts
    if len(frequencies_clean) > 10:
        trim_start = max(2, int(len(frequencies_clean) * 0.05))
        trim_end = max(2, int(len(frequencies_clean) * 0.10))
        frequencies_clean = frequencies_clean[trim_start:-trim_end]

    # Applies smoothing only on the isolated, stable vowel core    
    if len(frequencies_clean) > window_length:
        frequencies_clean = _smooth_curve(frequencies_clean, window_length=window_length)
    return frequencies_clean


def _prepare_for_dtw(series_clean: np.ndarray) -> np.ndarray:
    if len(series_clean) == 0:
        return np.array([])

    std_dev = np.std(series_clean)

    if std_dev == 0:
        return np.zeros((len(series_clean), 1))

    # Z-score normalization: removes pitch height differences (male vs female)
    # and scales contour dynamics so DTW only compares tone shapes.
    std_clamped = max(std_dev, 10.0)
    normalized = (series_clean - np.mean(series_clean)) / std_clamped
    # fastdtw expects a 2D array to work
    return normalized.reshape(-1, 1)


def process_audio(audio_path: Path) -> np.ndarray:
    pitch_object = _extract_pitch_data(audio_path)
    frequencies_clean = _get_clean_frequencies(pitch_object)
    dtw_ready_data = _prepare_for_dtw(frequencies_clean)
    return dtw_ready_data