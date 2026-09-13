import logging
import numpy as np
import sounddevice as sd
from pathlib import Path
from mandarinstudio.config import AUDIO_FOLDER
from scipy.io.wavfile import write

logger = logging.getLogger(__name__)
audio_path = AUDIO_FOLDER / 'user_audio.wav'

# remove silêncio no início e fim do áudio
def trim_audio_data(audio_data: np.ndarray, threshold: float=0.05) -> np.ndarray:
    # verifica se valores positivos do áudio são maiores que o limite de ruídos
    mask = np.abs(audio_data) > threshold
    if not np.any(mask):
        return audio_data

    start_idx = np.argmax(mask)
    end_idx = len(mask) - np.argmax(mask[::-1])
    return audio_data[start_idx:end_idx]


# gravação de áudio do usuário
def record_audio(audio_path=audio_path, duration: float=2, sample_rate: int=16000) -> Path:
    print('>>> Fale a sílaba...')
    audio_raw = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    logger.info('Gravação finalizada.')

    audio_trimmed = trim_audio_data(audio_raw.flatten())
    audio_int16 = (audio_trimmed * 32767).astype(np.int16)

    write(audio_path, sample_rate, audio_int16)
    logger.debug(f"Tamanho original: {len(audio_raw)} | Após limpeza: {len(audio_trimmed)}")
    return audio_path