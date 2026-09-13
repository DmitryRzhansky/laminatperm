"""Temporary public-site password gate (admin area is excluded)."""

from __future__ import annotations

import hmac

from flask import Flask, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired

SESSION_KEY = "site_gate_ok"
NEXT_KEY = "site_gate_next"


class SiteGateForm(FlaskForm):
    password = PasswordField("Пароль", validators=[DataRequired()])


def _is_exempt_path(path: str) -> bool:
    if path.startswith("/admin"):
        return True
    if path.startswith("/static"):
        return True
    return False


def _safe_next_url() -> str:
    candidate = session.pop(NEXT_KEY, None)
    if not candidate or not isinstance(candidate, str):
        return url_for("main.home")
    if not candidate.startswith("/") or candidate.startswith("//"):
        return url_for("main.home")
    if candidate.startswith("/admin") or candidate.startswith("/site-gate"):
        return url_for("main.home")
    return candidate.rstrip("?") or url_for("main.home")


def register_site_gate(app: Flask) -> None:
    @app.route("/site-gate", methods=["GET", "POST"])
    def site_gate():
        if not app.config.get("SITE_GATE_ENABLED", True):
            return redirect(url_for("main.home"))

        if session.get(SESSION_KEY):
            return redirect(_safe_next_url())

        form = SiteGateForm()
        error = None
        if form.validate_on_submit():
            expected = app.config.get("SITE_GATE_PASSWORD") or "admin"
            submitted = form.password.data or ""
            if hmac.compare_digest(submitted, expected):
                session[SESSION_KEY] = True
                return redirect(_safe_next_url())
            error = "Неверный пароль"

        return render_template("public/site_gate.html", form=form, error=error)

    @app.before_request
    def enforce_site_gate():
        if not app.config.get("SITE_GATE_ENABLED", True):
            return None
        if session.get(SESSION_KEY):
            return None
        if request.endpoint == "site_gate":
            return None
        if _is_exempt_path(request.path or "/"):
            return None

        if request.method in {"GET", "HEAD"}:
            next_path = request.full_path
            if next_path.endswith("?"):
                next_path = next_path[:-1]
            session[NEXT_KEY] = next_path

        return redirect(url_for("site_gate"))
