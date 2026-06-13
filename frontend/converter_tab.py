import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from backend.config import AVAILABLE_MODELS
from backend.converter import Converter
from backend.upscaler import Upscaler
from backend.pipeline import ProcessingPipeline
from backend.models import ImageJob
from backend.settings import Settings
from .styles import *


class ConverterTab(ttk.Frame):
    def __init__(self, parent, settings: Settings, converter: Converter,
                 upscaler: Upscaler, pipeline: ProcessingPipeline):
        super().__init__(parent)
        self.settings = settings
        self.converter = converter
        self.upscaler = upscaler
        self.pipeline = pipeline

        self.input_files = []
        self.output_folder = self.settings.get("output_folder", "")
        self.mode = tk.StringVar(value=self.settings.get("mode", "png_to_jpeg"))
        self.upscale_enabled = tk.BooleanVar(value=self.settings.get("upscale_enabled", False))
        self.upscale_model = tk.StringVar(value=self.settings.get("upscale_model", AVAILABLE_MODELS[0]))
        self.upscale_scale = tk.StringVar(value=self.settings.get("upscale_scale", "4"))
        self._processing = False

        self.upscale_model.trace_add("write", lambda *_: self.settings.set("upscale_model", self.upscale_model.get()))
        self.upscale_scale.trace_add("write", lambda *_: self.settings.set("upscale_scale", self.upscale_scale.get()))

        self.build_ui()

    def build_ui(self):
        self.title_label = tk.Label(self, text="Bulk Image Converter", font=FONT_TITLE)
        self.title_label.pack(pady=5)

        mode_frame = tk.Frame(self)
        mode_frame.pack(pady=5)
        tk.Label(mode_frame, text="Conversion Mode:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        rb_png2jpg = tk.Radiobutton(mode_frame, text="PNG \u2192 JPEG", variable=self.mode,
                                     value="png_to_jpeg", command=self.update_ui_for_mode)
        rb_png2jpg.pack(side=tk.LEFT, padx=5)
        rb_jpg2png = tk.Radiobutton(mode_frame, text="JPEG \u2192 PNG", variable=self.mode,
                                     value="jpeg_to_png", command=self.update_ui_for_mode)
        rb_jpg2png.pack(side=tk.LEFT, padx=5)

        self.lbl_select_instruction = tk.Label(self, font=FONT_SECTION)
        self.lbl_select_instruction.pack(pady=5)

        self.btn_select_files = tk.Button(self, command=self.select_files, width=25,
                                           bg=BG_PRIMARY, fg=COLOR_WHITE, font=FONT_BUTTON)
        self.btn_select_files.pack(pady=5)

        self.lbl_input_status = tk.Label(self, text="No files selected", fg=COLOR_GRAY)
        self.lbl_input_status.pack()

        self.btn_select_output = tk.Button(self, text="2. Select Output Folder",
                                            command=self.select_output_folder, width=25,
                                            bg=BG_SECONDARY, fg=COLOR_WHITE, font=FONT_BUTTON)
        self.btn_select_output.pack(pady=5)

        self.lbl_output_status = tk.Label(self, text="No output folder selected", fg=COLOR_GRAY)
        self.lbl_output_status.pack()

        sep = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        sep.pack(fill=tk.X, pady=8)

        self.chk_upscale = tk.Checkbutton(self, text="Enable AI Upscaling", variable=self.upscale_enabled,
                                           font=FONT_SECTION, command=self.toggle_upscale_ui)
        self.chk_upscale.pack(pady=2)

        self.upscale_frame = tk.Frame(self)
        tk.Label(self.upscale_frame, text="Scale:", font=FONT_SECTION).pack(side=tk.LEFT, padx=5)
        self.scale_spinbox = tk.Spinbox(self.upscale_frame, from_=1, to=10,
                                         textvariable=self.upscale_scale, width=4, font=FONT_SECTION)
        self.scale_spinbox.pack(side=tk.LEFT, padx=2)
        tk.Label(self.upscale_frame, text="x", font=FONT_SECTION).pack(side=tk.LEFT)
        tk.Label(self.upscale_frame, text="  Model:", font=FONT_SECTION).pack(side=tk.LEFT, padx=5)
        self.model_dropdown = ttk.Combobox(self.upscale_frame, textvariable=self.upscale_model,
                                            values=AVAILABLE_MODELS, state="readonly", width=20)
        self.model_dropdown.pack(side=tk.LEFT)

        if self.upscale_enabled.get():
            self.upscale_frame.pack(pady=3)

        self.btn_convert = tk.Button(self, command=self.convert_images, width=25,
                                      bg=BG_ACTION, fg=COLOR_WHITE, font=FONT_BUTTON_ACTION)
        self.btn_convert.pack(pady=10)

        self.lbl_progress = tk.Label(self, text="", fg=COLOR_GRAY, font=FONT_LABEL)
        self.lbl_progress.pack()

        self.update_ui_for_mode()
        self.restore_output_ui()

    def restore_output_ui(self):
        if self.output_folder:
            self.lbl_output_status.config(text=f"Output: {self.output_folder}", fg=COLOR_BLUE)

    def toggle_upscale_ui(self):
        self.settings.set("upscale_enabled", self.upscale_enabled.get())
        if self.upscale_enabled.get():
            self.upscale_frame.pack(pady=3)
        else:
            self.upscale_frame.pack_forget()

    def update_ui_for_mode(self):
        self.converter.configure(self.mode.get())
        self.settings.set("mode", self.mode.get())
        target = self.converter.target_name()
        source = "PNG" if target == "JPEG" else "JPEG"
        self.title_label.config(text=f"Bulk {source} to {target} Converter")
        self.lbl_select_instruction.config(text=f"Select {source} files to convert to {target}")
        self.btn_select_files.config(text=f"1. Select {source} Files")
        self.btn_convert.config(text=f"3. Convert to {target}")

    def select_files(self):
        self.converter.configure(self.mode.get())
        filetypes = self.converter.source_filetypes()
        paths = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
        if paths:
            self.input_files = list(paths)
            self.lbl_input_status.config(text=f"Selected {len(self.input_files)} image(s)", fg=COLOR_BLUE)

    def select_output_folder(self):
        initial = self.output_folder if self.output_folder else None
        folder = filedialog.askdirectory(title="Select Output Folder", initialdir=initial)
        if folder:
            self.output_folder = folder
            self.settings.set("output_folder", folder)
            self.lbl_output_status.config(text=f"Output: {self.output_folder}", fg=COLOR_BLUE)

    def _set_ui_enabled(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.btn_select_files.config(state=state)
        self.btn_select_output.config(state=state)
        self.btn_convert.config(state=state)
        self.chk_upscale.config(state=state)

    def convert_images(self):
        if self._processing:
            return
        if not self.input_files:
            messagebox.showwarning("Warning", "Please select images first!")
            return
        if not self.output_folder:
            messagebox.showwarning("Warning", "Please select the output folder first!")
            return
        if self.upscale_enabled.get() and not Upscaler.is_available():
            messagebox.showerror("Error", "Upscayl binary not found. Please check the installation.")
            return

        self.converter.configure(self.mode.get())
        self.upscaler.model = self.upscale_model.get()
        self.upscaler.scale = int(self.upscale_scale.get())

        self._processing = True
        self._set_ui_enabled(False)
        self.lbl_progress.config(text="Starting...")

        thread = threading.Thread(target=self._process_files, daemon=True)
        thread.start()

    def _update_progress(self, text):
        self.winfo_toplevel().after(0, lambda: self.lbl_progress.config(text=text))

    def _process_files(self):
        errors = []
        success_count = 0
        total = len(self.input_files)

        for idx, path in enumerate(self.input_files):
            base_name = os.path.basename(path)
            name = os.path.splitext(base_name)[0]

            job = ImageJob(
                source_path=path,
                output_dir=self.output_folder,
                output_name=name,
                mode=self.mode.get(),
                upscale_enabled=self.upscale_enabled.get(),
                upscale_model=self.upscale_model.get(),
                upscale_scale=int(self.upscale_scale.get()),
            )

            self._update_progress(f"Processing ({idx+1}/{total}): {name}")

            result = self.pipeline.process(job, on_progress=self._update_progress)
            if result.success:
                success_count += 1
            else:
                errors.append(result.error or f"Image {idx+1}: unknown error")

        self.winfo_toplevel().after(0, lambda: self._on_processing_done(success_count, errors))

    def _on_processing_done(self, success_count, errors):
        self._processing = False
        self._set_ui_enabled(True)
        self.lbl_progress.config(text="")

        target = self.converter.target_name()
        msg = f"Successfully converted {success_count} image(s) to {target}."
        if self.upscale_enabled.get():
            msg += f"\nOnly upscaled versions (_{self.upscale_scale.get()}x) saved."
        if errors:
            msg += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n... and {len(errors) - 5} more."
        messagebox.showinfo("Complete", msg)

        self.input_files = []
        self.lbl_input_status.config(text="No files selected", fg=COLOR_GRAY)
