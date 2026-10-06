import os
import yt_dlp


def download_video(url, output_path="downloads", quality="best", progress_hook=None):
    """
    Скачивает видео с Rutube через yt-dlp.

    :param url: ссылка на видео (публичная или приватная)
    :param output_path: папка для сохранения
    :param quality: 'best', '1080', '720', '480', '360'
    :param progress_hook: функция обратного вызова для прогресса
    :return: полный путь к файлу или None
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
        "nocheckcertificate": True,
    }

    if quality != "best":
        ydl_opts["format"] = (
            f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        )

    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith(".mp4"):
                base, _ = os.path.splitext(filename)
                candidate = base + ".mp4"
                if os.path.exists(candidate):
                    filename = candidate
            return filename
    except Exception as e:
        return f"ERROR: {e}"
