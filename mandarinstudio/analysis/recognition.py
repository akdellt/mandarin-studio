import wave
import json
import pypinyin

from mandarinstudio.config import VOSK_MODEL
from pathlib import Path
from vosk import Model, KaldiRecognizer

model_vosk = Model(str(VOSK_MODEL))

def check_spoken_pinyin(audio_path: Path, expected_hanzi: str, grammar: list[str] | None = None) -> bool:
    if not expected_hanzi or not expected_hanzi.strip():
        return False
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        with wave.open(str(audio_path), "rb") as wf:
            # grammar: restricts Vosk's search graph to a small list of expected words
            if grammar:
                vocab = list(grammar)
                # [unk]: unknown token to catch background noise or unexpected words
                if "[unk]" not in vocab:
                    vocab.append("[unk]")
                grammar_json = json.dumps(vocab, ensure_ascii=False)
                rec = KaldiRecognizer(model_vosk, wf.getframerate(), grammar_json)
            else:
                rec = KaldiRecognizer(model_vosk, wf.getframerate())

            audio_bytes = wf.readframes(wf.getnframes())
            rec.AcceptWaveform(audio_bytes)
    except wave.Error as err:
        raise ValueError(f"Fail to read WAV file: {err}") from err

    try:
        result = json.loads(rec.FinalResult())
    except json.JSONDecodeError:
        return False
    
    recognized_hanzi = result.get("text", "").replace(" ", "")
    if not recognized_hanzi or recognized_hanzi == "[unk]":
        return False

    # Removes tones to validate only if phoneme was spoken correctly
    recognized_pinyin_flat = "".join(
        j for i in pypinyin.pinyin(recognized_hanzi, style=pypinyin.Style.NORMAL) for j in i
    )
    expected_pinyin_flat = "".join(
        j for i in pypinyin.pinyin(expected_hanzi, style=pypinyin.Style.NORMAL) for j in i
    )

    is_correct = (recognized_pinyin_flat == expected_pinyin_flat) and len(recognized_pinyin_flat) > 0
    return is_correct