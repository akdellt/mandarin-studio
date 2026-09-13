import wave
import json
import pypinyin
from mandarinstudio.config import VOSK_MODEL
from pathlib import Path
from vosk import Model, KaldiRecognizer

model_vosk = Model(str(VOSK_MODEL))

# verifica se áudio contém sílaba a comparar
def check_spoken_pinyin(audio_path: Path, expected_pinyin: str) -> tuple[bool, str, str]:
    wf = wave.open(str(audio_path), "rb")
    rec = KaldiRecognizer(model_vosk, wf.getframerate())
    data = wf.readframes(wf.getnframes())
    rec.AcceptWaveform(data)

    result = json.loads(rec.FinalResult())
    hanzi = result.get("text", "").replace(" ", "")

    pinyin_with_tone = pypinyin.pinyin(hanzi, style=pypinyin.Style.TONE3)
    pinyin_display = " ".join(j for i in pinyin_with_tone for j in i)

    is_correct = pinyin_display == expected_pinyin
    return is_correct, pinyin_display, hanzi