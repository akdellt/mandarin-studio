import uuid

from pypinyin import pinyin, Style
from mandarinstudio.audio.reference import generate_audio_ref
from mandarinstudio.flashcards.models import Flashcard

def generate_pinyin(hanzi: str) -> str:
    pinyin_syllables = pinyin(hanzi, style=Style.TONE)
    return " ".join(syllable[0] for syllable in pinyin_syllables)

def create_flashcard(
    hanzi: str, 
    meaning: str, 
    grammar: list[str] | None = None, 
    phrase_example: str | None = None, 
    hsk_level: int | None = None
) -> Flashcard:
    flashcard_id = str(uuid.uuid4())

    pinyin_text  = generate_pinyin(hanzi)
    reference_audio_path = generate_audio_ref(hanzi, filename=flashcard_id)

    effective_grammar = grammar if grammar is not None else [hanzi]

    return Flashcard(
        id=flashcard_id,
        hanzi=hanzi,
        pinyin=pinyin_text,
        meaning=meaning,
        reference_audio_path=reference_audio_path,
        grammar=effective_grammar,
        phrase_example=phrase_example,
        hsk_level=hsk_level,
    )