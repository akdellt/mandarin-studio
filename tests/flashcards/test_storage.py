import pytest

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from mandarinstudio.flashcards.models import Flashcard
from mandarinstudio.flashcards.storage import (
    delete_flashcard,
    load_all_flashcards,
    load_flashcard,
    save_flashcard,
)


@pytest.fixture
def temp_storage(tmp_path: Path):
    cards_dir = tmp_path / "flashcards"
    with patch("mandarinstudio.flashcards.storage.FLASHCARDS_DIR", cards_dir):
        yield cards_dir


@pytest.fixture
def sample_card(tmp_path: Path) -> Flashcard:
    audio_path = tmp_path / "audio_ref.wav"
    audio_path.touch()

    return Flashcard(
        id="card-uuid-1234",
        hanzi="猫",
        pinyin="māo",
        meaning="gato",
        reference_audio_path=audio_path,
        grammar=["猫", "毛"],
        created_at=datetime.now(timezone.utc),
    )



def test_save_and_load_flashcard_success(temp_storage: Path, sample_card: Flashcard):
    saved_path = save_flashcard(sample_card)

    assert saved_path.is_file()
    assert saved_path.name == f"{sample_card.id}.json"

    loaded = load_flashcard(sample_card.id)

    assert loaded.id == sample_card.id
    assert loaded.hanzi == sample_card.hanzi
    assert loaded.pinyin == sample_card.pinyin
    assert isinstance(loaded.reference_audio_path, Path)
    assert loaded.reference_audio_path == sample_card.reference_audio_path
    assert isinstance(loaded.created_at, datetime)
    assert loaded.grammar == ["猫", "毛"]


def test_load_flashcard_not_found(temp_storage: Path):
    with pytest.raises(FileNotFoundError):
        load_flashcard("non-existent-id")


def test_load_flashcard_corrupted_json(temp_storage: Path):
    temp_storage.mkdir(parents=True, exist_ok=True)
    corrupted_file = temp_storage / "corrupted.json"
    corrupted_file.write_text("{invalid_content: true", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid file"):
        load_flashcard("corrupted")



def test_load_all_flashcards_sorted_and_ignores_corrupt(
    temp_storage: Path,
    sample_card: Flashcard,
    tmp_path: Path,
):
    card1 = sample_card

    card2 = Flashcard(
        id="card-uuid-5678",
        hanzi="狗",
        pinyin="gǒu",
        meaning="cachorro",
        reference_audio_path=tmp_path / "audio2.wav",
        grammar=["狗", "够"],
        created_at=datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc),
    )

    save_flashcard(card2)
    save_flashcard(card1)

    # Writes a corrupted JSON file to verify that load_all skips it
    (temp_storage / "garbage.json").write_text("corrupted_payload", encoding="utf-8")

    loaded_list = load_all_flashcards()

    assert len(loaded_list) == 2
    assert loaded_list[0].id == card2.id
    assert loaded_list[1].id == card1.id



def test_delete_flashcard_removes_json_and_audio(
    temp_storage: Path,
    sample_card: Flashcard,
):
    """Garante exclusão física do arquivo de metadados e do áudio atrelado."""
    save_flashcard(sample_card)
    audio_file = sample_card.reference_audio_path

    assert audio_file.is_file()
    assert (temp_storage / f"{sample_card.id}.json").is_file()

    success = delete_flashcard(sample_card.id, remove_audio=True)

    assert success is True
    assert not (temp_storage / f"{sample_card.id}.json").exists()
    assert not audio_file.exists()


def test_delete_flashcard_keep_audio(temp_storage: Path, sample_card: Flashcard):
    save_flashcard(sample_card)
    audio_file = sample_card.reference_audio_path

    delete_flashcard(sample_card.id, remove_audio=False)

    assert not (temp_storage / f"{sample_card.id}.json").exists()
    assert audio_file.is_file()


def test_delete_non_existent_flashcard(temp_storage: Path):
    assert delete_flashcard("non-existent-id") is False