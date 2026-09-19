import logging
import numpy as np
import sounddevice as sd

from pathlib import Path
from scipy.io.wavfile import write

from mandarinstudio.config import AUDIO_DIR

logger = logging.getLogger(__name__)

def _trim_audio_data(audio_data: np.ndarray, threshold: float=0.05) -> np.ndarray:
    # Finds audio samples where amplitude exceeds the ambient noise threshold
    mask = np.abs(audio_data) > threshold
    if not np.any(mask):
        return audio_data

    # First and last indices where audio exceeds threshold (trims start/end silence)
    start_idx = np.argmax(mask)
    end_idx = len(mask) - np.argmax(mask[::-1])
    return audio_data[start_idx:end_idx]


def record_audio(audio_path: Path | None = None, duration: float=2, sample_rate: int=16000) -> Path:
    target_path = audio_path or (AUDIO_DIR / "user_audio.wav")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        print('>>> Say the word...')
        audio_raw = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        logger.info('Record finished.')
    except sd.PortAudioError as err:
        logger.error(f"Error to access microphone: {err}")
        raise RuntimeError(
            "No microphone available or audio device inaccessible."
            "Check if the microphone is connected and permitted by the system."
        ) from err

    audio_trimmed = _trim_audio_data(audio_raw.flatten())

    # Fallback: keep unedited audio if silence detection trimmed the entire signal
    if len(audio_trimmed) == 0:
        logger.warning("No sound detected during silence trimming; keeping original audio.")
        audio_trimmed = audio_raw.flatten()

    # Prevents clipping/distortion before 16-bit integer scaling
    audio_clipped = np.clip(audio_trimmed, -1.0, 1.0)
    # Converts normalized float32 to signed PCM 16-bit required by Vosk and Praat
    audio_int16 = (audio_clipped * 32767).astype(np.int16)

    try:
        write(str(target_path), sample_rate, audio_int16)
        logger.debug(f"Original size: {len(audio_raw)} | After cleaning: {len(audio_trimmed)}")
    except OSError as err:
        raise IOError(f"Failed to save audio file in {target_path}: {err}") from err

    return target_path