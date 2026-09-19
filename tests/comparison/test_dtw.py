import numpy as np
import pytest

from pathlib import Path
from unittest.mock import patch

from mandarinstudio.comparison.dtw import run_dtw

@pytest.fixture
def dummy_paths(tmp_path: Path):
    ref = tmp_path / "ref.wav"
    user = tmp_path / "user.wav"
    ref.touch()
    user.touch()
    return ref, user


def test_run_dtw_identical_audio(dummy_paths):
    ref_path, user_path = dummy_paths
    mock_pitch = np.array([[0.1], [0.1], [0.1], [0.1]], dtype=np.float64)

    with patch("mandarinstudio.comparison.dtw.pitch.process_audio", return_value=mock_pitch):
        result = run_dtw(ref_path, user_path)

    assert result.avg_distance == pytest.approx(0.0)
    assert len(result.path) > 0
    assert not np.isinf(result.avg_distance)


def test_run_dtw_empty_pitch_returns_inf(dummy_paths):
    ref_path, user_path = dummy_paths
    valid_pitch = np.array([[0.5], [0.2], [-0.1]], dtype=np.float64)
    empty_pitch = np.array([], dtype=np.float64)

    with patch("mandarinstudio.comparison.dtw.pitch.process_audio", side_effect=[valid_pitch, empty_pitch]):
        result = run_dtw(ref_path, user_path)
        assert np.isinf(result.avg_distance)
        assert result.path == []

    with patch("mandarinstudio.comparison.dtw.pitch.process_audio", side_effect=[empty_pitch, valid_pitch]):
        result = run_dtw(ref_path, user_path)
        assert np.isinf(result.avg_distance)
        assert result.path == []


def test_run_dtw_different_contours(dummy_paths):
    ref_path, user_path = dummy_paths
    
    flat_pitch = np.zeros((10, 1), dtype=np.float64)
    falling_pitch = np.linspace(1.5, -1.5, 10).reshape(-1, 1)

    with patch("mandarinstudio.comparison.dtw.pitch.process_audio", side_effect=[flat_pitch, falling_pitch]):
        result = run_dtw(ref_path, user_path)

    assert result.avg_distance > 0.5
    assert len(result.path) >= 10