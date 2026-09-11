from __future__ import annotations

from app.extensions import db
from app.models.settings import SiteSetting


def get_setting(key: str, default: str = "") -> str:
    row = SiteSetting.query.filter_by(key=key).first()
    if row is None or row.value is None:
        return default
    return row.value


def set_setting(key: str, value: str) -> None:
    row = SiteSetting.query.filter_by(key=key).first()
    if row is None:
        row = SiteSetting(key=key, value=value or "")
        db.session.add(row)
    else:
        row.value = value or ""


def settings_map(prefix: str | None = None) -> dict[str, str]:
    query = SiteSetting.query
    if prefix:
        query = query.filter(SiteSetting.key.startswith(prefix))
    return {row.key: row.value for row in query.all()}
