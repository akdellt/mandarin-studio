import json
import logging

from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from mandarinstudio.flashcards.models import Flashcard
from mandarinstudio.config import FLASHCARDS_DIR

logger = logging.getLogger(__name__)

def _ensure_folder_exists() -> None:
    FLASHCARDS_DIR.mkdir(parents=True, exist_ok=True)


def _flashcard_file_path(flashcard_id: str) -> Path:
    return FLASHCARDS_DIR / f"{flashcard_id}.json"


def _deserialize_flashcard(data: dict) -> Flashcard:
    # Restores non-primitive objects from serialized strings
    data["reference_audio_path"] = Path(data["reference_audio_path"])
    data["created_at"] = datetime.fromisoformat(data["created_at"])
    return Flashcard(**data)



def save_flashcard(flashcard: Flashcard) -> Path:
    _ensure_folder_exists()

    data = asdict(flashcard)
    # Converts non-serializable objects (Path, datetime) into JSON primitives
    data["reference_audio_path"] = str(flashcard.reference_audio_path)
    data["created_at"] = flashcard.created_at.isoformat()

    file_path = _flashcard_file_path(flashcard.id)
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), 
        encoding="utf-8"
    )
    logger.debug(f"Flashcard successfully saved: {file_path}")
    return file_path


def load_flashcard(flashcard_id: str) -> Flashcard:
    file_path = _flashcard_file_path(flashcard_id)

    if not file_path.is_file():
        raise FileNotFoundError(f"Flashcard with id '{flashcard_id}' not found in {file_path}")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return _deserialize_flashcard(data)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as err:
        logger.error(f"Flashcard file invalid or corrupted: {file_path} - {err}")
        raise ValueError(f"Unable to load flashcard '{flashcard_id}': invalid file.") from err


def load_all_flashcards() -> list[Flashcard]:
    _ensure_folder_exists()

    flashcards: list[Flashcard] = []
    for file_path in FLASHCARDS_DIR.glob("*.json"):
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            flashcards.append(_deserialize_flashcard(data))
        except Exception as err:
            # Skips corrupt JSON files instead of aborting batch load
            logger.warning(f"Ignoring corrupted flashcard in {file_path.name}: {err}")
            continue

    # Preserves card creation sequence (oldest first)
    flashcards.sort(key=lambda card: card.created_at)
    return flashcards


def delete_flashcard(flashcard_id: str, remove_audio: bool = True) -> bool:
    file_path = _flashcard_file_path(flashcard_id)

    if not file_path.is_file():
        return False

    # 1:1 binding (UUID): safely purges the dedicated reference audio to prevent orphan files
    if remove_audio:
        try:
            card = load_flashcard(flashcard_id)
            if card.reference_audio_path.is_file():
                card.reference_audio_path.unlink()
                logger.debug(f"Reference audio removed: {card.reference_audio_path}")
        except Exception as err:
            logger.warning(f"Not possible to delete audio of flashcard {flashcard_id}: {err}")

    # Guarantees the JSON metadata is deleted even if audio resolution failed
    file_path.unlink()
    logger.info(f"Flashcard {flashcard_id} successfully deleted.")
    return True