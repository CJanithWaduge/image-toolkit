from __future__ import annotations

import logging
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List

from backend.rag_engine import MetadataResult, RAGEngine
from . import styles as S

logger = logging.getLogger(__name__)


class MetadataTab(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.engine = RAGEngine()
        self._image_files: list[str] = []
        self._results: List[MetadataResult] = []
        self._processing = False
        self._lock = threading.Lock()

        self.build_ui()

    def build_ui(self) -> None:
        tk.Label(self, text="Metadata Generator", font=S.FONT_TITLE).pack(pady=8)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=6)

        self.btn_images = tk.Button(
            btn_frame, text="Select Images", command=self.select_image_files,
            width=22, bg=S.BG_PRIMARY, fg=S.COLOR_WHITE, font=S.FONT_BUTTON,
        )
        self.btn_images.pack(side=tk.LEFT, padx=4)

        self.btn_generate = tk.Button(
            btn_frame, text="Generate All", command=self.generate_all,
            width=22, bg=S.BG_ACTION, fg=S.COLOR_WHITE, font=S.FONT_BUTTON,
            state=tk.DISABLED,
        )
        self.btn_generate.pack(side=tk.LEFT, padx=4)

        self.btn_clear = tk.Button(
            btn_frame, text="Clear", command=self.clear_selection,
            width=8, bg=S.COLOR_GRAY, fg=S.COLOR_WHITE, font=S.FONT_BUTTON,
            state=tk.DISABLED,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=4)

        self.btn_download = tk.Button(
            btn_frame, text="Download .txt", command=self.download_results,
            width=22, bg=S.BG_ACCENT, fg=S.COLOR_WHITE, font=S.FONT_BUTTON,
            state=tk.DISABLED,
        )
        self.btn_download.pack(side=tk.LEFT, padx=4)

        self.lbl_image_status = tk.Label(self, text="No images selected", fg=S.COLOR_GRAY, font=S.FONT_LABEL)
        self.lbl_image_status.pack(pady=2)

        tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=6)

        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.txt_results = tk.Text(
            text_frame, wrap=tk.WORD, font=("Consolas", 9),
            yscrollcommand=scrollbar.set, state=tk.DISABLED,
        )
        self.txt_results.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.txt_results.yview)

        self.lbl_progress = tk.Label(self, text="", fg=S.COLOR_GRAY, font=S.FONT_LABEL)
        self.lbl_progress.pack(pady=4)

    def select_image_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select Image(s)",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")],
        )
        if not paths:
            return
        self._image_files = list(paths)
        self._results = []
        self.lbl_image_status.config(
            text=f"{len(self._image_files)} image(s) selected",
            fg=S.COLOR_BLUE,
        )
        self.btn_generate.config(state=tk.NORMAL)
        self.btn_clear.config(state=tk.NORMAL)
        self.btn_download.config(state=tk.DISABLED)

        self.txt_results.config(state=tk.NORMAL)
        self.txt_results.delete("1.0", tk.END)
        self.txt_results.insert(tk.END, f"Selected {len(self._image_files)} image(s):\n")
        for p in self._image_files:
            self.txt_results.insert(tk.END, f"  {p}\n")
        self.txt_results.insert(tk.END, "\nClick Generate All to start.\n")
        self.txt_results.config(state=tk.DISABLED)
        self.lbl_progress.config(text="Ready. Click Generate All.")

    def clear_selection(self) -> None:
        self._image_files = []
        self._results = []
        self.lbl_image_status.config(text="No images selected", fg=S.COLOR_GRAY)
        self.btn_generate.config(state=tk.DISABLED)
        self.btn_clear.config(state=tk.DISABLED)
        self.btn_download.config(state=tk.DISABLED)
        self.txt_results.config(state=tk.NORMAL)
        self.txt_results.delete("1.0", tk.END)
        self.txt_results.config(state=tk.DISABLED)
        self.lbl_progress.config(text="")

    def generate_all(self) -> None:
        if not self._lock.acquire(blocking=False):
            return
        try:
            if self._processing:
                return
            if not self._image_files:
                messagebox.showwarning("Warning", "Please select images first!")
                return

            self._processing = True
            self.btn_generate.config(state=tk.DISABLED)
            self.btn_images.config(state=tk.DISABLED)
            self.btn_clear.config(state=tk.DISABLED)
            self.btn_download.config(state=tk.DISABLED)
            self.lbl_progress.config(text="Starting...")

            thread = threading.Thread(target=self._run, daemon=True)
            thread.start()
        finally:
            self._lock.release()

    def _run(self) -> None:
        try:
            def on_progress(current: int, total: int, message: str) -> None:
                self._update_progress(current, total, message)

            results = self.engine.generate_from_files(
                self._image_files,
                on_progress=on_progress,
            )
            self._results = results
            self.winfo_toplevel().after(0, lambda: self._show_results(results))
        except Exception as e:
            logger.exception("Generation failed")
            self.winfo_toplevel().after(0, lambda: self._show_error(str(e)))

    def _show_results(self, results: List[MetadataResult]) -> None:
        self.txt_results.config(state=tk.NORMAL)
        self.txt_results.delete("1.0", tk.END)

        for i, r in enumerate(results, 1):
            self.txt_results.insert(tk.END, f"{i}.\n")
            self.txt_results.insert(tk.END, f"title: {r.title}\n")
            self.txt_results.insert(tk.END, f"Tags: {', '.join(r.tags)}\n")
            desc = r.description[:197] + "..." if len(r.description) > 200 else r.description
            self.txt_results.insert(tk.END, f"Description: {desc}\n\n")

        self.txt_results.config(state=tk.DISABLED)
        self._set_buttons_idle()
        self.lbl_progress.config(text=f"Done — {len(results)} image(s) processed")

    def _show_error(self, msg: str) -> None:
        self._set_buttons_idle()
        self.lbl_progress.config(text="")
        messagebox.showerror("Error", f"Generation failed:\n{msg}")

    def download_results(self) -> None:
        if not self._results:
            messagebox.showwarning("Warning", "No results to download. Generate first!")
            return

        path = filedialog.asksaveasfilename(
            title="Save results as",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )
        if not path:
            return

        try:
            content = RAGEngine.format_download(self._results)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Results saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def _set_buttons_idle(self) -> None:
        self._processing = False
        self.btn_generate.config(state=tk.NORMAL)
        self.btn_images.config(state=tk.NORMAL)
        if self._image_files:
            self.btn_clear.config(state=tk.NORMAL)

    def _update_progress(self, current: int, total: int, message: str) -> None:
        prefix = f"[{current}/{total}] " if total > 0 else ""
        self.winfo_toplevel().after(0, lambda: self.lbl_progress.config(text=f"{prefix}{message}"))
