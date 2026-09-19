from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass
class Flashcard:
    # required
    id: str
    hanzi: str
    pinyin: str
    meaning: str
    reference_audio_path: Path

    # optionals
    grammar: list[str] = field(default_factory=list)
    phrase_example: str | None = None
    hsk_level: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)