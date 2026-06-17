import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.config import UPSCAYL_EXE, UPSCAYL_MODELS, RESOURCES_DIR, MODEL_LIST


def test_resources_dir_exists():
    assert os.path.isdir(RESOURCES_DIR)


def test_upscayl_bin_exists():
    assert os.path.isfile(UPSCAYL_EXE)


def test_models_dir_exists():
    assert os.path.isdir(UPSCAYL_MODELS)


def test_available_models_not_empty():
    assert len(MODEL_LIST) > 0


def test_each_model_has_bin_and_param():
    for model in MODEL_LIST:
        bin_path = os.path.join(UPSCAYL_MODELS, f"{model}.bin")
        param_path = os.path.join(UPSCAYL_MODELS, f"{model}.param")
        assert os.path.isfile(bin_path), f"Missing .bin for {model}"
        assert os.path.isfile(param_path), f"Missing .param for {model}"
