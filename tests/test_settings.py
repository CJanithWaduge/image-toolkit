import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.settings import Settings


class TestSettings:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.settings_path = Path(self.tmpdir) / "settings.json"
        self.patcher = patch.object(Settings, "_FILE", self.settings_path)
        self.patcher.start()

    def teardown_method(self):
        self.patcher.stop()

    def test_get_default(self):
        s = Settings()
        assert s.get("nonexistent", "default") == "default"

    def test_set_and_get(self):
        s = Settings()
        s.set("theme", "dark")
        assert s.get("theme") == "dark"

    def test_persists_across_instances(self):
        s1 = Settings()
        s1.set("key1", "value1")
        s2 = Settings()
        assert s2.get("key1") == "value1"

    def test_load_returns_empty_dict_on_missing_file(self):
        s = Settings()
        assert s.data == {}
