from PIL import Image


class Converter:
    def __init__(self):
        self.source_ext = ".png"
        self.target_ext = ".jpeg"
        self.target_format = "JPEG"
        self.convert_to_rgb = True

    def configure(self, mode):
        if mode == "png_to_jpeg":
            self.source_ext = ".png"
            self.target_ext = ".jpeg"
            self.target_format = "JPEG"
            self.convert_to_rgb = True
        else:
            self.source_ext = (".jpg", ".jpeg")
            self.target_ext = ".png"
            self.target_format = "PNG"
            self.convert_to_rgb = False

    def convert(self, input_path, output_path):
        img = Image.open(input_path)
        if self.convert_to_rgb:
            img = img.convert("RGB")
        img.save(output_path, self.target_format)

    def source_filetypes(self):
        if self.target_format == "JPEG":
            return [("PNG Files", "*.png")]
        return [("JPEG Files", "*.jpg *.jpeg")]

    def target_name(self):
        return "JPEG" if self.target_format == "JPEG" else "PNG"
