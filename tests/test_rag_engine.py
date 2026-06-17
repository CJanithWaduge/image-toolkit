import os
import sys
import tempfile
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.rag_engine import RAGEngine, MetadataResult
from backend.vision import LocalVisionEngine


SAMPLE_PROMPTS = """1. a serene mountain landscape at sunset with purple skies
2. futuristic cyberpunk city with neon lights and flying cars
3. cute fluffy cat sleeping on a cozy blanket
"""


def _create_test_image(path, size=(10, 10), mode="RGB"):
    img = Image.new(mode, size, (255, 0, 0))
    img.save(path)


class TestRAGEngine:
    def setup_method(self):
        self.engine = RAGEngine()
        self.tmpdir = tempfile.mkdtemp()

    def _write_prompts(self, content):
        path = os.path.join(self.tmpdir, "prompts.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_parse_prompts_numbered(self):
        path = self._write_prompts(SAMPLE_PROMPTS)
        prompts = self.engine.parse_prompts(path)
        assert len(prompts) == 3
        assert "mountain" in prompts[0]
        assert "cyberpunk" in prompts[1]
        assert "cat" in prompts[2]

    def test_parse_prompts_single_block(self):
        path = self._write_prompts("just a single prompt without numbers")
        prompts = self.engine.parse_prompts(path)
        assert len(prompts) == 1
        assert prompts[0] == "just a single prompt without numbers"

    def test_parse_valid_json(self):
        raw = '{"title": "Test", "tags": ["tag1", "tag2"], "description": "A test description"}'
        result = self.engine._parse(raw)
        assert result.title == "Test"
        assert result.tags == ["tag1", "tag2"]
        assert result.description == "A test description"

    def test_parse_invalid_json(self):
        raw = "not json at all"
        result = self.engine._parse(raw)
        assert result.title == "Parse error"
        assert result.tags == []
        assert len(result.description) <= 200

    def test_parse_partial_json(self):
        raw = 'some text {"title": "Partial"} trailing'
        result = self.engine._parse(raw)
        assert result.title == "Partial"

    def test_format_download(self):
        results = [
            MetadataResult(title="Title1", tags=["a", "b"], description="Desc1"),
            MetadataResult(title="Title2", tags=["c"], description="Desc2"),
        ]
        output = RAGEngine.format_download(results)
        assert "1." in output
        assert "title: Title1" in output
        assert "Tags: a, b" in output
        assert "Description: Desc1" in output
        assert "2." in output
        assert "title: Title2" in output

    def test_resolve_image_found_png(self):
        _create_test_image(os.path.join(self.tmpdir, "1.png"))
        path = RAGEngine._resolve_image(1, self.tmpdir)
        assert path == os.path.join(self.tmpdir, "1.png")

    def test_resolve_image_found_jpg(self):
        _create_test_image(os.path.join(self.tmpdir, "2.jpg"))
        path = RAGEngine._resolve_image(2, self.tmpdir)
        assert path == os.path.join(self.tmpdir, "2.jpg")

    def test_resolve_image_not_found(self):
        path = RAGEngine._resolve_image(99, self.tmpdir)
        assert path is None

    def test_resolve_image_nonexistent_folder(self):
        path = RAGEngine._resolve_image(1, "C:\\nonexistent_folder_xyz")
        assert path is None

    def test_vision_describe_returns_string(self):
        img_path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(img_path, mode="RGB")
        desc = LocalVisionEngine.describe(img_path)
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_vision_is_available(self):
        assert LocalVisionEngine.is_available() is True

    def test_vision_describe_includes_objects(self):
        img_path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(img_path, mode="RGB")
        desc = LocalVisionEngine.describe(img_path)
        assert "Dominant colors" in desc
        assert any(word in desc for word in ("background", "red", "white"))


