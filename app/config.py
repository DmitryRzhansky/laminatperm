import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _default_database_uri() -> str:
    instance_dir = BASE_DIR / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)
    return "sqlite:///" + (instance_dir / "app.db").resolve().as_posix()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or _default_database_uri()
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
    # Temporary public-site password gate (admin area stays open).
    SITE_GATE_ENABLED = os.getenv("SITE_GATE_ENABLED", "1") in {"1", "true", "True"}
    SITE_GATE_PASSWORD = os.getenv("SITE_GATE_PASSWORD", "admin")
    # Public site origin for canonical / Open Graph / JSON-LD absolute URLs.
    # Example: https://laminashion.ru — without trailing slash.
    SITE_URL = (os.getenv("SITE_URL") or "").rstrip("/")
    WTF_CSRF_ENABLED = True

    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
    UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_DEBUG", "0") not in {"1", "true", "True"}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "secret"
    SITE_GATE_ENABLED = False

