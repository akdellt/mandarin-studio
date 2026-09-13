# google: gerar/buscar áudio de referencia
from pathlib import Path
from gtts import gTTS
from mandarinstudio.config import AUDIO_FOLDER

def generate_audio_ref(hanzi: str) -> Path:
    tts = gTTS(hanzi, lang='zh-CN',)
    audio_path = AUDIO_FOLDER / f'{hanzi}.wav'
    tts.save(audio_path)
    return audio_path