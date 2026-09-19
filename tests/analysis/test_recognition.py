import pytest

from pathlib import Path
from mandarinstudio.analysis.recognition import check_spoken_pinyin

@pytest.fixture
def fixtures_dir() -> Path:
    path = Path(__file__).parent / "fixtures" / "user"
    if not path.exists():
        path = Path(__file__).parent.parent / "fixtures" / "user"
    return path


def test_check_spoken_pinyin_exact_match(fixtures_dir: Path):
    audio_path = fixtures_dir / "ma_tone2.wav"
    
    if not audio_path.exists():
        pytest.skip("Fixture file 'ma_tone2.wav' not found.")

    grammar = ["妈", "麻", "马"]
    
    result = check_spoken_pinyin(
        audio_path=audio_path,
        expected_hanzi="妈",
        grammar=grammar
    )

    assert result is True


def test_check_spoken_pinyin_wrong_syllable(fixtures_dir: Path):
    audio_path = fixtures_dir / "ma_tone1.wav"

    if not audio_path.exists():
        pytest.skip("Fixture file 'ma_tone1.wav' not found.")

    grammar = ["妈", "麻", "马"]

    result = check_spoken_pinyin(
        audio_path=audio_path,
        expected_hanzi="猫",
        grammar=grammar
    )

    assert result is False


def test_check_spoken_pinyin_different_tone_same_syllable(fixtures_dir: Path):
    audio_path = fixtures_dir / "ma_tone1.wav"

    if not audio_path.exists():
        pytest.skip("Fixture file 'ma_tone1.wav' not found.")
    
    grammar = ["妈", "麻", "马"]

    result = check_spoken_pinyin(
        audio_path=audio_path,
        expected_hanzi="马",
        grammar=grammar
    )

    assert result is True


def test_check_spoken_pinyin_file_not_found():
    non_existent_audio = Path("fixtures/arquivo_que_nao_existe.wav")

    with pytest.raises(FileNotFoundError):
        check_spoken_pinyin(non_existent_audio, expected_hanzi="麻")


def test_check_spoken_pinyin_empty_expected_hanzi(fixtures_dir: Path):
    audio_path = fixtures_dir / "ma_tone1.wav"
    
    if not audio_path.exists():
        pytest.skip("Fixture file 'ma_tone1.wav' not found.")

    assert check_spoken_pinyin(audio_path, expected_hanzi="") is False
    assert check_spoken_pinyin(audio_path, expected_hanzi="   ") is False

