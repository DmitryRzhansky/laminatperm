"""Catalog image helpers: lossless WebP conversion and SEO filenames."""

from __future__ import annotations

import io
from pathlib import Path

from flask import current_app
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.utils.files import ALLOWED_IMAGE_EXTENSIONS, allowed_file
from app.utils.slugs import slugify

CATALOG_REL_DIR = "uploads/catalog"


def catalog_upload_dir() -> Path:
    return Path(current_app.config["UPLOAD_FOLDER"]) / "catalog"


def product_image_stem(product, index: int = 0) -> str:
    """Build SEO stem: kupit-{product-slug}-v-permi[-N]."""
    base_slug = slugify(getattr(product, "slug", "") or getattr(product, "name", "") or "tovar")
    stem = f"kupit-{base_slug}-v-permi"
    if index > 0:
        stem = f"{stem}-{index + 1}"
    return stem


def unique_catalog_path(stem: str, *, exclude: Path | None = None) -> Path:
    folder = catalog_upload_dir()
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{stem}.webp"
    if exclude is not None and target.resolve() == exclude.resolve() and target.exists():
        return target
    counter = 2
    while target.exists() and (exclude is None or target.resolve() != exclude.resolve()):
        target = folder / f"{stem}-{counter}.webp"
        counter += 1
    return target


def _prepare_image(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "RGB"}:
        return image
    if image.mode == "P":
        return image.convert("RGBA")
    if image.mode == "LA":
        return image.convert("RGBA")
    if image.mode == "L":
        return image.convert("RGB")
    if image.mode == "CMYK":
        return image.convert("RGB")
    return image.convert("RGBA")


def convert_file_to_lossless_webp(source: Path, destination: Path) -> Path:
    """Convert an image file to lossless WebP. Returns destination path."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        prepared = _prepare_image(image)
        prepared.save(destination, format="WEBP", lossless=True, method=6)
    return destination


def convert_bytes_to_lossless_webp(data: bytes, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(io.BytesIO(data)) as image:
        prepared = _prepare_image(image)
        prepared.save(destination, format="WEBP", lossless=True, method=6)
    return destination


def static_relative(path: Path) -> str:
    static_root = path
    while static_root.name != "static" and static_root.parent != static_root:
        static_root = static_root.parent
    return path.relative_to(static_root).as_posix()


def absolute_from_static_relative(relative: str) -> Path | None:
    text = (relative or "").strip().lstrip("/")
    if not text:
        return None
    if text.startswith("static/"):
        text = text[len("static/") :]
    static_root = Path(current_app.static_folder)
    return static_root / text


def optimize_product_image(image_row, product, index: int) -> bool:
    """
    Convert a ProductImage to lossless WebP with SEO filename.
    Returns True when filename or file changed.
    """
    source_path = absolute_from_static_relative(image_row.filename)
    if source_path is None or not source_path.exists():
        return False

    stem = product_image_stem(product, index)
    destination = unique_catalog_path(stem, exclude=source_path)
    same_path = source_path.resolve() == destination.resolve()
    already_webp = source_path.suffix.lower() == ".webp"

    if same_path and already_webp:
        # Re-encode to ensure lossless WebP, writing via temp then replace.
        temp = destination.with_suffix(".tmp.webp")
        convert_file_to_lossless_webp(source_path, temp)
        temp.replace(destination)
        new_rel = static_relative(destination)
        changed = image_row.filename != new_rel
        image_row.filename = new_rel
        return changed

    convert_file_to_lossless_webp(source_path, destination)
    new_rel = static_relative(destination)
    changed = image_row.filename != new_rel
    image_row.filename = new_rel

    if source_path.resolve() != destination.resolve() and source_path.exists():
        try:
            source_path.unlink()
        except OSError:
            pass

    return True


def save_catalog_product_image(file: FileStorage, product, index: int = 0) -> str | None:
    """Save an uploaded image as lossless SEO-named WebP under uploads/catalog."""
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return None

    data = file.read()
    if not data:
        return None

    destination = unique_catalog_path(product_image_stem(product, index))
    try:
        convert_bytes_to_lossless_webp(data, destination)
    except OSError:
        return None
    return static_relative(destination)


def save_catalog_image_bytes(data: bytes, product, index: int = 0) -> str | None:
    if not data:
        return None
    destination = unique_catalog_path(product_image_stem(product, index))
    try:
        convert_bytes_to_lossless_webp(data, destination)
    except OSError:
        return None
    return static_relative(destination)
