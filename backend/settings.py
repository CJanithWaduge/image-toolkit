from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class Settings:
    _FILE: Path = Path(
        os.environ.get("APPDATA", Path.home())
    ) / "ImageConverter" / "settings.json"

    def __init__(self) -> None:
        self.data: dict = self._load()

    def _load(self) -> dict:
        try:
            with open(self._FILE, encoding="utf-8") as f:
                return dict(json.load(f))
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logger.warning("Corrupt settings file (%s), starting fresh", self._FILE)
            return {}

    def save(self) -> None:
        self._FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self._FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key: str, default: object = None) -> object:
        return self.data.get(key, default)

    def set(self, key: str, value: object) -> None:
        self.data[key] = value
        self.save()
