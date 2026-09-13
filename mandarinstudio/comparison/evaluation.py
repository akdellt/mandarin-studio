import logging
import numpy as np
from pathlib import Path
from enum import Enum
from typing import NamedTuple
from mandarinstudio.analysis import recognition
from mandarinstudio.comparison.dtw import run_dtw

logger = logging.getLogger(__name__)

class CategoryOptions(Enum):
    PERFECT = "perfect"
    EXCELLENT = "excellent"
    MODERATE = "moderate"
    INCORRECT = "incorrect"

class ComparisonMetrics(NamedTuple):
    avg_distance: float
    is_correct: bool
    spoken_pinyin: str
    hanzi: str

class PronunciationResult(NamedTuple):
    category: CategoryOptions
    similarity: float
    spoken_pinyin: str
    hanzi: str

MAX_ACCEPTABLE_DISTANCE = 0.8


def compare_audio(ref_audio: Path, user_audio: Path, target_pinyin: str) -> ComparisonMetrics:
    dtw_result  = run_dtw(ref_audio, user_audio)
    avg_distance = np.inf if not dtw_result.path else dtw_result.distance / len(dtw_result.path)

    logger.debug(f"Distância Média por Frame: {avg_distance:.4f}")

    is_correct, spoken_pinyin, hanzi = recognition.check_spoken_pinyin(user_audio, target_pinyin)
    return ComparisonMetrics(avg_distance, is_correct, spoken_pinyin, hanzi)


def evaluate_pronunciation(ref_audio: Path, user_audio: Path, target_pinyin: str) -> PronunciationResult:
    metrics = compare_audio(ref_audio, user_audio, target_pinyin)
    similarity = max(0.0, 100 - ((metrics.avg_distance * 100) / MAX_ACCEPTABLE_DISTANCE))

    if similarity >= 90:
        category  = CategoryOptions.PERFECT
    elif similarity >= 70:
        category  = CategoryOptions.EXCELLENT
    elif similarity >= 50:
        category  = CategoryOptions.MODERATE
    else:
        category  = CategoryOptions.INCORRECT

    if not metrics.is_correct and category == CategoryOptions.PERFECT:
        category = CategoryOptions.EXCELLENT
    return PronunciationResult(category, similarity, metrics.spoken_pinyin, metrics.hanzi)