import threading
import os
import sys

import customtkinter as ctk
from tkinter import filedialog, Menu
from PIL import Image

from downloader import download_video

APP_NAME = "i. Rutube Downloader"
FONT = "Unbounded Medium"

WHITE = "#ffffff"
BLACK = "#000000"
GREY = "#8a8a8a"
LINE = "#e0e0e0"

GIF_HEIGHT = 52


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


GIF_PATH = resource_path("tenor.gif")


def font(size):
    return (FONT, size)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("680x540")
        self.resizable(False, False)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=WHITE)

        self.title_label = ctk.CTkLabel(
            self,
            text="i.",
            font=font(40),
            text_color=BLACK,
            fg_color=WHITE,
        )
        self.title_label.pack(pady=(34, 0))

        self.sub_label = ctk.CTkLabel(
            self,
            text="rutube downloader",
            font=font(13),
            text_color=GREY,
            fg_color=WHITE,
        )
        self.sub_label.pack(pady=(2, 18))

        self.label = ctk.CTkLabel(
            self,
            text="Ссылка на видео",
            font=font(12),
            text_color=BLACK,
            fg_color=WHITE,
        )
        self.label.pack(anchor="w", padx=70, pady=(0, 6))

        self.url_row = ctk.CTkFrame(self, fg_color=WHITE)
        self.url_row.pack(pady=0)

        self.url_entry = ctk.CTkEntry(
            self.url_row,
            width=440,
            height=40,
            placeholder_text="https://rutube.ru/video/...",
            font=font(12),
            fg_color=WHITE,
            border_color=BLACK,
            border_width=1,
            text_color=BLACK,
            placeholder_text_color=GREY,
            corner_radius=0,
        )
        self.url_entry.pack(side="left", padx=(70, 0))
        self.url_entry.bind("<Control-v>", self.paste_url)
        self.url_entry.bind("<Control-V>", self.paste_url)
        self.url_entry.bind("<Button-3>", self.show_url_menu)

        self.paste_button = ctk.CTkButton(
            self.url_row,
            text="Вставить",
            width=110,
            height=40,
            font=font(12),
            fg_color=BLACK,
            hover_color="#333333",
            text_color=WHITE,
            corner_radius=0,
            command=self.paste_url,
        )
        self.paste_button.pack(side="left")

        self.options_row = ctk.CTkFrame(self, fg_color=WHITE)
        self.options_row.pack(pady=18, fill="x", padx=70)

        self.quality_label = ctk.CTkLabel(
            self.options_row,
            text="КАЧЕСТВО",
            font=font(10),
            text_color=GREY,
            fg_color=WHITE,
        )
        self.quality_label.pack(side="left")
        self.quality_var = ctk.StringVar(value="best")
        self.quality_menu = ctk.CTkOptionMenu(
            self.options_row,
            variable=self.quality_var,
            values=["best", "1080", "720", "480", "360"],
            width=120,
            height=32,
            font=font(12),
            fg_color=WHITE,
            button_color=BLACK,
            button_hover_color="#333333",
            dropdown_fg_color=WHITE,
            dropdown_hover_color=LINE,
            dropdown_text_color=BLACK,
            text_color=BLACK,
            corner_radius=0,
        )
        self.quality_menu.pack(side="left", padx=(12, 0))

        self.folder_label = ctk.CTkLabel(
            self.options_row,
            text="ПАПКА",
            font=font(10),
            text_color=GREY,
            fg_color=WHITE,
        )
        self.folder_label.pack(side="left", padx=(28, 0))
        self.folder_entry = ctk.CTkEntry(
            self.options_row,
            width=200,
            height=32,
            placeholder_text="downloads",
            font=font(12),
            fg_color=WHITE,
            border_color=BLACK,
            border_width=1,
            text_color=BLACK,
            placeholder_text_color=GREY,
            corner_radius=0,
        )
        self.folder_entry.insert(0, "downloads")
        self.folder_entry.pack(side="left", padx=(12, 0))

        self.folder_button = ctk.CTkButton(
            self.options_row,
            text="...",
            width=36,
            height=32,
            font=font(12),
            fg_color=WHITE,
            hover_color=LINE,
            text_color=BLACK,
            border_color=BLACK,
            border_width=1,
            corner_radius=0,
            command=self.choose_folder,
        )
        self.folder_button.pack(side="left")

        self.open_folder_var = ctk.BooleanVar(value=True)
        self.open_folder_check = ctk.CTkCheckBox(
            self,
            text="Открывать папку после скачивания",
            variable=self.open_folder_var,
            font=font(11),
            text_color=BLACK,
            fg_color=BLACK,
            border_color=BLACK,
            checkmark_color=WHITE,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=0,
            hover_color="#555555",
        )
        self.open_folder_check.pack(anchor="w", padx=70, pady=(4, 0))

        self.download_button = ctk.CTkButton(
            self,
            text="СКАЧАТЬ",
            font=font(15),
            height=48,
            width=540,
            fg_color=BLACK,
            hover_color="#333333",
            text_color=WHITE,
            corner_radius=0,
            command=self.start_download,
        )
        self.download_button.pack(pady=(24, 0), padx=70)

        self.progress_row = ctk.CTkFrame(self, fg_color=WHITE)
        self.progress_row.pack(pady=(18, 0), padx=70, fill="x")

        self.gif_label = ctk.CTkLabel(
            self.progress_row, text="", width=58, height=GIF_HEIGHT, fg_color=WHITE
        )
        self.gif_label.pack(side="left", padx=(0, 10))

        self.progress = ctk.CTkProgressBar(
            self.progress_row,
            progress_color=BLACK,
            fg_color=LINE,
            corner_radius=0,
            height=4,
        )
        self.progress.set(0)
        self.progress.pack(side="left", fill="x", expand=True)

        self.gif_frames = []
        self.gif_delays = []
        self.gif_index = 0
        self.gif_running = False
        self.gif_job = None
        self.load_gif()

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=font(10),
            wraplength=540,
            justify="center",
            text_color=GREY,
            fg_color=WHITE,
        )
        self.status_label.pack(pady=(10, 0))

        self.url_entry.focus_set()

    def load_gif(self):
        if not os.path.exists(GIF_PATH):
            return
        try:
            image = Image.open(GIF_PATH)
            self.gif_delays = []
            frames = []
            for index in range(getattr(image, "n_frames", 1)):
                image.seek(index)
                frame = image.convert("RGBA")
                width = int(frame.width * GIF_HEIGHT / frame.height)
                frame = frame.resize((width, GIF_HEIGHT), Image.LANCZOS)
                frames.append(ctk.CTkImage(light_image=frame, size=(width, GIF_HEIGHT)))
                self.gif_delays.append(max(image.info.get("duration", 100) or 100, 20))
            self.gif_frames = frames
            if self.gif_frames:
                self.gif_label.configure(image=self.gif_frames[0])
        except Exception:
            self.gif_frames = []

    def start_gif(self):
        if not self.gif_frames:
            return
        self.gif_running = True
        self.gif_index = 0
        self.animate_gif()

    def stop_gif(self):
        self.gif_running = False
        if self.gif_job is not None:
            try:
                self.after_cancel(self.gif_job)
            except Exception:
                pass
            self.gif_job = None
        if self.gif_frames:
            self.gif_label.configure(image=self.gif_frames[0])

    def animate_gif(self):
        if not self.gif_running or not self.gif_frames:
            return
        self.gif_label.configure(image=self.gif_frames[self.gif_index])
        delay = self.gif_delays[self.gif_index % len(self.gif_delays)]
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.gif_job = self.after(delay, self.animate_gif)

    def paste_url(self, event=None):
        try:
            text = self.clipboard_get()
        except Exception:
            return "break" if event else None
        text = str(text).strip()
        if text:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, text)
            self.set_status("ссылка вставлена", BLACK)
        if event:
            return "break"

    def show_url_menu(self, event):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="Вставить", command=self.paste_url)
        menu.add_command(label="Копировать", command=self.copy_url)
        menu.add_command(label="Выделить всё", command=self.select_url_all)
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def copy_url(self):
        text = self.url_entry.get().strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)

    def select_url_all(self):
        self.url_entry.focus_set()
        self.url_entry.select_range(0, "end")
        self.url_entry.icursor("end")

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def set_status(self, text, color):
        def update():
            self.status_label.configure(text=text, text_color=color)

        self.after(0, update)

    def set_progress(self, value):
        def update():
            self.progress.set(value)

        self.after(0, update)

    def set_button_state(self, state):
        def update():
            self.download_button.configure(state=state)

        self.after(0, update)

    def on_progress(self, d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if total:
                self.set_progress(downloaded / total)
                percent = downloaded / total * 100
                self.set_status(f"скачивание {percent:.1f}%", BLACK)
        elif d.get("status") == "finished":
            self.set_progress(1)
            self.set_status("завершено, обработка...", BLACK)

    def open_folder(self, path):
        try:
            target = path if os.path.isdir(path) else os.path.dirname(os.path.abspath(path))
            if target and os.path.isdir(target):
                os.startfile(target)
        except Exception:
            pass

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.set_status("вставьте ссылку", "#c0392b")
            return

        quality = self.quality_var.get()
        output_path = self.folder_entry.get().strip() or "downloads"

        self.download_button.configure(state="disabled")
        self.progress.set(0)
        self.set_status("скачивание...", BLACK)
        self.after(0, self.start_gif)

        thread = threading.Thread(
            target=self.run_download, args=(url, output_path, quality), daemon=True
        )
        thread.start()

    def run_download(self, url, output_path, quality):
        result = download_video(url, output_path, quality, progress_hook=self.on_progress)
        self.after(0, self.stop_gif)
        if result and not str(result).startswith("ERROR:"):
            self.set_status(f"готово — {os.path.basename(result)}", BLACK)
            self.set_progress(1)
            if self.open_folder_var.get():
                self.after(400, lambda: self.open_folder(result))
        else:
            msg = str(result) if result else "неизвестная ошибка"
            self.set_status(f"ошибка: {msg}", "#c0392b")
            self.set_progress(0)
        self.set_button_state("normal")
