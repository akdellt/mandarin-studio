from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

CURRENT_FILE = Path(__file__).resolve()

ROOT_PROJECT = CURRENT_FILE.parent.parent

DATA_FOLDER = ROOT_PROJECT / "data"
AUDIO_FOLDER = DATA_FOLDER / "audio_mock"
VOSK_MODEL = DATA_FOLDER / "model" / "vosk-model-cn-0.22"