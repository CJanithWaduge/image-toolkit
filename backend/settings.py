import json
import os
from pathlib import Path


class Settings:
    _FILE = Path(os.environ.get("APPDATA", Path.home())) / "ImageConverter" / "settings.json"

    def __init__(self):
        self.data = self._load()

    def _load(self):
        try:
            with open(self._FILE, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self):
        self._FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self._FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
