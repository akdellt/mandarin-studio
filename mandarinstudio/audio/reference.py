import logging
import io

from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment

from mandarinstudio.config import AUDIO_REF_DIR

logger = logging.getLogger(__name__)

def _convert_mp3_bytes_to_wav(mp3_buffer: io.BytesIO, target_path: Path) -> Path:
    mp3_buffer.seek(0)
    sound = AudioSegment.from_mp3(mp3_buffer)
    sound = sound.set_channels(1).set_frame_rate(16000)
    sound.export(str(target_path), format="wav")
    return target_path


def generate_audio_ref(hanzi: str, filename: str) -> Path:
    if not hanzi or not hanzi.strip():
        raise ValueError("The hanzi cannot be empty.")
    hanzi = hanzi.strip()

    AUDIO_REF_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = AUDIO_REF_DIR / f"{filename}.wav"

    # Cache hit: avoids unnecessary network requests and API rate limits
    if audio_path.exists() and audio_path.stat().st_size > 0:
        logger.debug(f"Reference audio in cache: {audio_path}")
        return audio_path
    
    try:
        logger.info(f"Generating reference audio via gTTS for: {hanzi}...")
        tts = gTTS(text=hanzi.strip(), lang="zh-CN")
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        # Converts mp3 format (gTTS) to wav format (Praat)
        _convert_mp3_bytes_to_wav(mp3_buffer, audio_path)
        logger.info(f"Reference audio successfully saved to: {audio_path}")
    except Exception as err:
        # Removes partially downloaded or corrupted files to keep the cache clean
        if audio_path.exists():
            try:
                audio_path.unlink()
            except OSError:
                pass

        logger.error(f"Failed to generate audio via gTTS for '{hanzi}': {err}")
        raise ConnectionError(
            f"Could not generate the reference audio for '{hanzi}'. "
            "Check your internet connection or try again later."
        ) from err

    return audio_path