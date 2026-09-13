import numpy as np
import parselmouth
from pathlib import Path
from scipy.signal import savgol_filter

# extrai a frequência (altura) do som
def extract_pitch_data(audio_path: Path) -> parselmouth.Pitch:
    audio = parselmouth.Sound(str(audio_path))
    pitch = audio.to_pitch(pitch_floor=75, pitch_ceiling=600)
    return pitch


# suaviza as frequências
def smooth_curve(frequencies: np.ndarray, window_length: int = 5, polyorder: int = 2) -> np.ndarray:
    if len(frequencies) <= window_length:
        return frequencies
    return savgol_filter(frequencies, window_length=window_length, polyorder=polyorder) # type: ignore[return-value]


# trata array de frequência para remover silêncio
def get_clean_frequencies(pitch_object: parselmouth.Pitch) -> np.ndarray:
    frequencies_raw = pitch_object.selected_array['frequency']
    frequencies_clean = frequencies_raw[(frequencies_raw > 0) & (~np.isnan(frequencies_raw))]

    if len(frequencies_clean) > 5:
        frequencies_clean = smooth_curve(frequencies_clean)
    return frequencies_clean


#  limpeza para algoritmo de comparação
def prepare_for_dtw(series: np.ndarray) -> np.ndarray:
    # remove NaNs
    series_clean = series[~np.isnan(series)]

    if len(series_clean) == 0:
        return np.array([])

    normalized = (series_clean - np.mean(series_clean)) / np.std(series_clean)
    return normalized.reshape(-1, 1)


# função completa de processamento
def process_audio(audio_path:Path) -> np.ndarray:
    pitch_raw = extract_pitch_data(audio_path)
    frequencies_clean = get_clean_frequencies(pitch_raw)
    dtw_ready_data = prepare_for_dtw(frequencies_clean)
    return dtw_ready_data

