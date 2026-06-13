import tkinter as tk
from tkinter import ttk

from backend.converter import Converter
from backend.upscaler import Upscaler
from backend.pipeline import ProcessingPipeline
from backend.settings import Settings
from .converter_tab import ConverterTab
from .metadata_tab import MetadataTab


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Toolkit")
        self.geometry("560x540")
        self.config(padx=10, pady=10)

        self.settings = Settings()
        self.converter = Converter()
        self.upscaler = Upscaler()
        self.pipeline = ProcessingPipeline(self.converter, self.upscaler)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        converter_tab = ConverterTab(notebook, self.settings, self.converter, self.upscaler, self.pipeline)
        converter_tab.pack(fill=tk.BOTH, expand=True)
        notebook.add(converter_tab, text="Converter")

        metadata_tab = MetadataTab(notebook)
        metadata_tab.pack(fill=tk.BOTH, expand=True)
        notebook.add(metadata_tab, text="Metadata Generator")
