from __future__ import annotations

from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}


def allowed_file(filename: str, allowed: set[str]) -> bool:
    return Path(filename).suffix.lower() in allowed


def save_upload(file: FileStorage, folder: Path, allowed: set[str] | None = None) -> str | None:
    if not file or not file.filename:
        return None

    allowed = allowed or ALLOWED_IMAGE_EXTENSIONS
    if not allowed_file(file.filename, allowed):
        return None

    folder.mkdir(parents=True, exist_ok=True)
    original = Path(secure_filename(file.filename))
    name = original.stem or "file"
    suffix = original.suffix.lower()
    target = folder / f"{name}{suffix}"
    counter = 2
    while target.exists():
        target = folder / f"{name}-{counter}{suffix}"
        counter += 1

    file.save(target)
    static_root = folder
    while static_root.name != "static" and static_root.parent != static_root:
        static_root = static_root.parent
    return target.relative_to(static_root).as_posix()
