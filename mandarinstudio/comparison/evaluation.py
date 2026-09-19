import logging

from pathlib import Path
from enum import Enum

from mandarinstudio.analysis import recognition
from mandarinstudio.comparison.dtw import run_dtw
from mandarinstudio.flashcards.models import Flashcard

logger = logging.getLogger(__name__)

class CategoryOptions(Enum):
    PERFECT = "perfect"
    EXCELLENT = "excellent"
    MODERATE = "moderate"
    INCORRECT = "incorrect"

# Empirical threshold: average Z-normalized DTW distance above which tone shape is considered wrong
MAX_ACCEPTABLE_DISTANCE = 0.8


def compare_audio(
    ref_audio: Path,
    user_audio: Path,
    target_hanzi: str,
    grammar: list[str] | None = None,
) -> tuple[float | None, bool]:
    is_correct = recognition.check_spoken_pinyin(user_audio, target_hanzi, grammar)

    # Skips pitch analysis if the basic phoneme was mispronounced
    if not is_correct:
        return None, False

    dtw_result  = run_dtw(ref_audio, user_audio)
    return dtw_result.avg_distance, True


def evaluate_pronunciation(flashcard: Flashcard, user_audio: Path) -> tuple[CategoryOptions, float]:
    if not isinstance(flashcard.hanzi, str) or not flashcard.hanzi.strip():
        raise ValueError("The flashcard's hanzi cannot be empty or invalid.")
    target_hanzi = flashcard.hanzi.strip()

    ref_audio = flashcard.reference_audio_path
    user_audio = Path(user_audio)

    if not ref_audio.is_file():
        raise FileNotFoundError(f"Reference audio not found or invalid: {ref_audio}")
    if not user_audio.is_file():
        raise FileNotFoundError(f"User recording not found or invalid: {user_audio}")

    grammar = flashcard.grammar
    avg_distance, is_correct = compare_audio(ref_audio, user_audio, target_hanzi, grammar)
    
    if not is_correct or avg_distance is None:
        return CategoryOptions.INCORRECT, 0.0
    
    # Maps DTW distance [0, MAX_ACCEPTABLE_DISTANCE] into a [100%, 0%] score
    similarity = max(0.0, 100 - ((avg_distance * 100) / MAX_ACCEPTABLE_DISTANCE))
    similarity = round(float(similarity), 2)
            
    if similarity >= 90:
        category  = CategoryOptions.PERFECT
    elif similarity >= 70:
        category  = CategoryOptions.EXCELLENT
    elif similarity >= 50:
        category  = CategoryOptions.MODERATE
    else:
        category  = CategoryOptions.INCORRECT

    return category, similarity