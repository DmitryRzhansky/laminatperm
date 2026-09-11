from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired
import hmac

from app.utils.auth import AdminUser

auth_bp = Blueprint("auth", __name__, url_prefix="/admin")


class LoginForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = current_app.config["ADMIN_USERNAME"]
        password = current_app.config["ADMIN_PASSWORD"]
        user_ok = hmac.compare_digest(form.username.data or "", username)
        pass_ok = hmac.compare_digest(form.password.data or "", password)
        if user_ok and pass_ok:
            login_user(AdminUser())
            next_url = request.args.get("next") or url_for("admin.dashboard")
            return redirect(next_url)
        flash("Неверный логин или пароль", "error")
    return render_template("admin/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
