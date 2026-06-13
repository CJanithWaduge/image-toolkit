import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dotenv import load_dotenv

from backend.rag_engine import RAGEngine, MetadataResult
from .styles import *

load_dotenv()


class MetadataTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.engine = RAGEngine()
        self._file_path: str = ""
        self._results: list[MetadataResult] = []
        self._processing = False

        self.build_ui()

    def build_ui(self):
        self.title_label = tk.Label(self, text="Metadata Generator", font=FONT_TITLE)
        self.title_label.pack(pady=8)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=6)

        self.btn_upload = tk.Button(
            btn_frame, text="Upload .txt File", command=self.upload_file,
            width=18, bg=BG_PRIMARY, fg=COLOR_WHITE, font=FONT_BUTTON,
        )
        self.btn_upload.pack(side=tk.LEFT, padx=4)

        self.btn_generate = tk.Button(
            btn_frame, text="Generate All", command=self.generate_bulk,
            width=18, bg=BG_ACTION, fg=COLOR_WHITE, font=FONT_BUTTON,
            state=tk.DISABLED,
        )
        self.btn_generate.pack(side=tk.LEFT, padx=4)

        self.btn_download = tk.Button(
            btn_frame, text="Download .txt", command=self.download_results,
            width=18, bg=BG_SECONDARY, fg=COLOR_WHITE, font=FONT_BUTTON,
            state=tk.DISABLED,
        )
        self.btn_download.pack(side=tk.LEFT, padx=4)

        self.lbl_file_status = tk.Label(self, text="No file selected", fg=COLOR_GRAY, font=FONT_LABEL)
        self.lbl_file_status.pack(pady=2)

        sep = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        sep.pack(fill=tk.X, pady=6)

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

        self.lbl_progress = tk.Label(self, text="", fg=COLOR_GRAY, font=FONT_LABEL)
        self.lbl_progress.pack(pady=4)

    def upload_file(self):
        path = filedialog.askopenfilename(
            title="Select .txt file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        self._file_path = path
        self._results = []

        try:
            prompts = self.engine.parse_prompts(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{e}")
            return

        name = os.path.basename(path)
        self.lbl_file_status.config(
            text=f"Loaded: {name} ({len(prompts)} prompt(s) detected)",
            fg=COLOR_BLUE,
        )
        self.btn_generate.config(state=tk.NORMAL)
        self.btn_download.config(state=tk.DISABLED)

        self.txt_results.config(state=tk.NORMAL)
        self.txt_results.delete("1.0", tk.END)

        for i, p in enumerate(prompts, 1):
            self.txt_results.insert(tk.END, f"{i}. {p[:80]}{'...' if len(p) > 80 else ''}\n")
        self.txt_results.config(state=tk.DISABLED)
        self.lbl_progress.config(text=f"{len(prompts)} prompt(s) loaded. Click Generate All.")

    def generate_bulk(self):
        if self._processing:
            return
        if not self._file_path:
            messagebox.showwarning("Warning", "Please upload a .txt file first!")
            return

        self._processing = True
        self.btn_generate.config(state=tk.DISABLED)
        self.btn_upload.config(state=tk.DISABLED)
        self.btn_download.config(state=tk.DISABLED)
        self.lbl_progress.config(text="Starting...")

        thread = threading.Thread(target=self._run_bulk, daemon=True)
        thread.start()

    def _run_bulk(self):
        try:
            self._update_progress("", "Indexing document...", 0, 0)

            def on_progress(current, total, message):
                self._update_progress(current, message, current, total)

            results = self.engine.generate_bulk(self._file_path, on_progress=on_progress)

            self._results = results
            self.winfo_toplevel().after(0, lambda: self._show_bulk_results(results))
        except Exception as e:
            self.winfo_toplevel().after(0, lambda: self._show_error(str(e)))

    def _show_bulk_results(self, results: list[MetadataResult]):
        self.txt_results.config(state=tk.NORMAL)
        self.txt_results.delete("1.0", tk.END)

        for i, r in enumerate(results, 1):
            self.txt_results.insert(tk.END, f"{i}.\n")
            self.txt_results.insert(tk.END, f"title: {r.title}\n")
            self.txt_results.insert(tk.END, f"Tags: {', '.join(r.tags)}\n")

            desc = (r.description[:197] + "...") if len(r.description) > 200 else r.description
            self.txt_results.insert(tk.END, f"Description: {desc}\n\n")

        self.txt_results.config(state=tk.DISABLED)

        self._set_buttons_normal()
        self.btn_download.config(state=tk.NORMAL)
        self.lbl_progress.config(text=f"Done — {len(results)} prompt(s) processed")

    def _show_error(self, msg):
        self._set_buttons_normal()
        self.lbl_progress.config(text="")
        messagebox.showerror("Error", f"Generation failed:\n{msg}")

    def download_results(self):
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

    def _set_buttons_normal(self):
        self._processing = False
        self.btn_generate.config(state=tk.NORMAL)
        self.btn_upload.config(state=tk.NORMAL)

    def _update_progress(self, current, message, idx=0, total=0):
        prefix = f"[{idx}/{total}] " if total > 0 else ""
        self.winfo_toplevel().after(0, lambda: self.lbl_progress.config(text=f"{prefix}{message}"))
