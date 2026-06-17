import os
import sys
import tempfile
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.converter import Converter


def _create_test_image(path, ext=".png", mode="RGBA"):
    img = Image.new(mode, (10, 10), (255, 0, 0, 255))
    img.save(path)


class TestConverter:
    def setup_method(self):
        self.converter = Converter()
        self.tmpdir = tempfile.mkdtemp()

    def test_default_mode_is_png_to_jpeg(self):
        assert self.converter.target_format == "JPEG"

    def test_configure_png_to_jpeg(self):
        self.converter.configure("png_to_jpeg")
        assert self.converter.source_ext == ".png"
        assert self.converter.target_ext == ".jpeg"
        assert self.converter.convert_to_rgb is True

    def test_configure_jpeg_to_png(self):
        self.converter.configure("jpeg_to_png")
        assert self.converter.source_ext == ".jpg"
        assert self.converter.target_ext == ".png"
        assert self.converter.convert_to_rgb is False

    def test_target_name_jpeg(self):
        self.converter.configure("png_to_jpeg")
        assert self.converter.target_name() == "JPEG"

    def test_target_name_png(self):
        self.converter.configure("jpeg_to_png")
        assert self.converter.target_name() == "PNG"

    def test_source_filetypes_png_to_jpeg(self):
        self.converter.configure("png_to_jpeg")
        types = self.converter.source_filetypes()
        assert types[0][1] == "*.png"

    def test_source_filetypes_jpeg_to_png(self):
        self.converter.configure("jpeg_to_png")
        types = self.converter.source_filetypes()
        assert types[0][1] == "*.jpg *.jpeg"

    def test_convert_png_to_jpeg(self):
        src = os.path.join(self.tmpdir, "test.png")
        dst = os.path.join(self.tmpdir, "test.jpeg")
        _create_test_image(src)
        self.converter.configure("png_to_jpeg")
        self.converter.convert(src, dst)
        assert os.path.isfile(dst)
        with Image.open(dst) as img:
            assert img.format == "JPEG"

    def test_convert_jpeg_to_png(self):
        src = os.path.join(self.tmpdir, "test.jpg")
        dst = os.path.join(self.tmpdir, "test.png")
        _create_test_image(src, ext=".jpg", mode="RGB")
        self.converter.configure("jpeg_to_png")
        self.converter.convert(src, dst)
        assert os.path.isfile(dst)
        with Image.open(dst) as img:
            assert img.format == "PNG"
