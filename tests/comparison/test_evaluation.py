import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch

from mandarinstudio.comparison.evaluation import (
    CategoryOptions,
    compare_audio,
    evaluate_pronunciation,
)
from mandarinstudio.flashcards.models import Flashcard


@pytest.fixture
def mock_flashcard(tmp_path: Path) -> Flashcard:
    ref_audio = tmp_path / "ref.wav"
    ref_audio.touch()

    return Flashcard(
        id="123e4567-e89b-12d3-a456-426614174000",
        hanzi="妈",
        pinyin="mā",
        meaning="mãe",
        reference_audio_path=ref_audio,
        grammar=["妈", "马", "猫"],
    )


@pytest.fixture
def dummy_user_audio(tmp_path: Path) -> Path:
    user_audio = tmp_path / "user.wav"
    user_audio.touch()
    return user_audio



def test_compare_audio_phoneme_mismatch(dummy_user_audio, mock_flashcard):
    with patch(
        "mandarinstudio.comparison.evaluation.recognition.check_spoken_pinyin",
        return_value=False,
    ), patch("mandarinstudio.comparison.evaluation.run_dtw") as mock_dtw:
        avg_dist, is_correct = compare_audio(
            ref_audio=mock_flashcard.reference_audio_path,
            user_audio=dummy_user_audio,
            target_hanzi=mock_flashcard.hanzi,
            grammar=mock_flashcard.grammar,
        )

    assert is_correct is False
    assert avg_dist is None
    mock_dtw.assert_not_called()


def test_compare_audio_phoneme_success(dummy_user_audio, mock_flashcard):
    mock_dtw_result = MagicMock(avg_distance=0.15)

    with patch(
        "mandarinstudio.comparison.evaluation.recognition.check_spoken_pinyin",
        return_value=True,
    ), patch(
        "mandarinstudio.comparison.evaluation.run_dtw",
        return_value=mock_dtw_result,
    ) as mock_dtw:
        avg_dist, is_correct = compare_audio(
            ref_audio=mock_flashcard.reference_audio_path,
            user_audio=dummy_user_audio,
            target_hanzi=mock_flashcard.hanzi,
            grammar=mock_flashcard.grammar,
        )

    assert is_correct is True
    assert avg_dist == 0.15
    mock_dtw.assert_called_once()



def test_evaluate_pronunciation_invalid_hanzi(mock_flashcard, dummy_user_audio):
    mock_flashcard.hanzi = "   "

    with pytest.raises(ValueError, match="cannot be empty or invalid"):
        evaluate_pronunciation(mock_flashcard, dummy_user_audio)


def test_evaluate_pronunciation_missing_audio_files(mock_flashcard, tmp_path: Path):
    missing_user_audio = tmp_path / "not_exists.wav"

    with pytest.raises(FileNotFoundError):
        evaluate_pronunciation(mock_flashcard, missing_user_audio)


@pytest.mark.parametrize(
    "avg_dist, expected_category, expected_score",
    [
        (0.04, CategoryOptions.PERFECT, 95.0),      # 100 - (0.04 * 100 / 0.8) = 95.0%
        (0.16, CategoryOptions.EXCELLENT, 80.0),    # 100 - (0.16 * 100 / 0.8) = 80.0%
        (0.36, CategoryOptions.MODERATE, 55.0),     # 100 - (0.36 * 100 / 0.8) = 55.0%
        (0.70, CategoryOptions.INCORRECT, 12.5),    # 100 - (0.70 * 100 / 0.8) = 12.5%
        (1.20, CategoryOptions.INCORRECT, 0.0),     # Over MAX_ACCEPTABLE_DISTANCE
    ],
)
def test_evaluate_pronunciation_scoring_categories(
    mock_flashcard,
    dummy_user_audio,
    avg_dist,
    expected_category,
    expected_score,
):
    with patch(
        "mandarinstudio.comparison.evaluation.compare_audio",
        return_value=(avg_dist, True),
    ):
        category, score = evaluate_pronunciation(mock_flashcard, dummy_user_audio)

    assert category == expected_category
    assert score == pytest.approx(expected_score, rel=1e-2)


def test_evaluate_pronunciation_phoneme_failed_returns_zero(
    mock_flashcard,
    dummy_user_audio,
):
    with patch(
        "mandarinstudio.comparison.evaluation.compare_audio",
        return_value=(None, False),
    ):
        category, score = evaluate_pronunciation(mock_flashcard, dummy_user_audio)

    assert category == CategoryOptions.INCORRECT
    assert score == 0.0