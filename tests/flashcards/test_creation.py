import uuid
from pathlib import Path
from unittest.mock import patch

from mandarinstudio.flashcards.creation import create_flashcard, generate_pinyin


def test_generate_pinyin_single_character():
    assert generate_pinyin("妈") == "mā"
    assert generate_pinyin("狗") == "gǒu"


def test_generate_pinyin_compound_word():
    assert generate_pinyin("你好") == "nǐ hǎo"


def test_create_flashcard_success_with_defaults(tmp_path: Path):
    fake_audio_path = tmp_path / "fake_audio.wav"

    with patch(
        "mandarinstudio.flashcards.creation.generate_audio_ref",
        return_value=fake_audio_path,
    ) as mock_audio_gen:
        card = create_flashcard(hanzi="猫", meaning="cat")

    # Verifies UUID format validity
    parsed_uuid = uuid.UUID(card.id, version=4)
    assert str(parsed_uuid) == card.id

    assert card.hanzi == "猫"
    assert card.pinyin == "māo"
    assert card.meaning == "cat"
    assert card.reference_audio_path == fake_audio_path
    assert card.phrase_example is None
    assert card.hsk_level is None

    assert card.grammar == ["猫"]

    mock_audio_gen.assert_called_once_with("猫", filename=card.id)


def test_create_flashcard_with_custom_optional_fields(tmp_path: Path):
    fake_audio_path = tmp_path / "custom_audio.wav"
    custom_grammar = ["猫", "毛"]

    with patch(
        "mandarinstudio.flashcards.creation.generate_audio_ref",
        return_value=fake_audio_path,
    ):
        card = create_flashcard(
            hanzi="猫",
            meaning="cat",
            grammar=custom_grammar,
            phrase_example="我有一只猫。",
            hsk_level=1,
        )

    assert card.grammar == ["猫", "毛"]
    assert card.phrase_example == "我有一只猫。"
    assert card.hsk_level == 1