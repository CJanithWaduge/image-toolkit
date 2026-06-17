import os
import sys
import tempfile
from unittest.mock import Mock, patch
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.converter import Converter
from backend.upscaler import Upscaler
from backend.pipeline import ProcessingPipeline
from backend.models import ImageJob


def _create_test_image(path):
    img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
    img.save(path)


class TestProcessingPipeline:
    def setup_method(self):
        self.converter = Converter()
        self.upscaler = Upscaler()
        self.pipeline = ProcessingPipeline(self.converter, self.upscaler)
        self.tmpdir = tempfile.mkdtemp()

    def test_process_conversion_only(self):
        src = os.path.join(self.tmpdir, "input.png")
        _create_test_image(src)
        job = ImageJob(
            source_path=src,
            output_dir=self.tmpdir,
            output_name="output",
            mode="png_to_jpeg",
            upscale_enabled=False,
        )
        result = self.pipeline.process(job)
        assert result.success is True
        assert result.output_path is not None
        assert result.output_path.endswith(".jpeg")
        assert os.path.isfile(result.output_path)

    def test_process_with_upscale(self):
        src = os.path.join(self.tmpdir, "input.png")
        _create_test_image(src)

        mock_upscaler = Mock(spec=Upscaler)
        mock_upscaler.upscale = Mock()

        pipeline = ProcessingPipeline(self.converter, mock_upscaler)
        job = ImageJob(
            source_path=src,
            output_dir=self.tmpdir,
            output_name="output",
            mode="png_to_jpeg",
            upscale_enabled=True,
        )
        result = pipeline.process(job)
        assert result.success is True
        mock_upscaler.upscale.assert_called_once()

    def test_process_returns_error_on_failure(self):
        result = self.pipeline.process(
            ImageJob(
                source_path="/nonexistent/input.png",
                output_dir=self.tmpdir,
                output_name="output",
                mode="png_to_jpeg",
            )
        )
        assert result.success is False
        assert result.error is not None

    def test_progress_callback_called(self):
        src = os.path.join(self.tmpdir, "input.png")
        _create_test_image(src)
        callback = Mock()
        job = ImageJob(
            source_path=src,
            output_dir=self.tmpdir,
            output_name="output",
            mode="png_to_jpeg",
            upscale_enabled=False,
        )
        self.pipeline.process(job, on_progress=callback)
        callback.assert_called()
