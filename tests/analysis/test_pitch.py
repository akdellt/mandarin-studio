import numpy as np
import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch
from mandarinstudio.analysis.pitch import process_audio

@pytest.fixture
def mock_pitch_object():
    mock_pitch = MagicMock()

    mock_frequencies = np.array([0.0, 0.0, 200.0, 202.0, 199.0, 201.0, 200.0, 203.0, 
                                 201.0, 199.0, 202.0, 200.0, 201.0, 200.0, 0.0])
    mock_pitch.selected_array = {"frequency": mock_frequencies}
    return mock_pitch


def test_process_audio_success_shape(tmp_path: Path, mock_pitch_object):
    dummy_wav = tmp_path / "sample.wav"
    dummy_wav.touch()

    with patch("mandarinstudio.analysis.pitch._extract_pitch_data", return_value=mock_pitch_object):
        result = process_audio(dummy_wav)

    assert isinstance(result, np.ndarray)
    assert result.ndim == 2
    assert result.shape[1] == 1
    assert len(result) > 0


def test_process_audio_completely_silent(tmp_path: Path):
    dummy_wav = tmp_path / "silent.wav"
    dummy_wav.touch()

    mock_silent_pitch = MagicMock()
    mock_silent_pitch.selected_array = {"frequency": np.zeros(20)}

    with patch("mandarinstudio.analysis.pitch._extract_pitch_data", return_value=mock_silent_pitch):
        result = process_audio(dummy_wav)

    assert isinstance(result, np.ndarray)
    assert result.size == 0


def test_process_audio_file_not_found():
    non_existent_file = Path("no/path/audio.wav")

    with pytest.raises(FileNotFoundError):
        process_audio(non_existent_file)


def test_process_audio_flat_tone_stability(tmp_path: Path):
    dummy_wav = tmp_path / "flat.wav"
    dummy_wav.touch()

    mock_flat_pitch = MagicMock()
    mock_flat_pitch.selected_array = {"frequency": np.full(30, 250.0)}

    with patch("mandarinstudio.analysis.pitch._extract_pitch_data", return_value=mock_flat_pitch):
        result = process_audio(dummy_wav)

    assert not np.isnan(result).any()
    assert not np.isinf(result).any()
    assert result.shape[1] == 1