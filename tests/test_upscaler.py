import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.upscaler import Upscaler


class TestUpscaler:
    def test_is_available_returns_true(self):
        assert Upscaler.is_available() is True

    def test_default_model(self):
        u = Upscaler()
        assert u.model == "remacri-4x"

    def test_default_scale(self):
        u = Upscaler()
        assert u.scale == 4

    def test_custom_model_and_scale(self):
        u = Upscaler(model="ultrasharp-4x", scale=2)
        assert u.model == "ultrasharp-4x"
        assert u.scale == 2
