from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"

FLASHCARDS_DIR = DATA_DIR / "flashcards"
AUDIO_DIR = DATA_DIR / "audio"
AUDIO_REF_DIR = AUDIO_DIR / "references"
AUDIO_USER_DIR = AUDIO_DIR / "recordings"
VOSK_MODEL = DATA_DIR / "model" / "vosk-model-cn-0.22"

for folder in [FLASHCARDS_DIR, AUDIO_REF_DIR, AUDIO_USER_DIR]:
    folder.mkdir(parents=True, exist_ok=True)