from pathlib import Path

from flask import Flask
from flask_login import current_user
from flask_wtf.csrf import generate_csrf

from app.config import Config
from app.extensions import csrf, db, login_manager, migrate
from app.utils.auth import AdminUser
from app.utils.markdown import render_markdown
from app.utils.settings import get_setting
from app.services.cart import CartService


def create_app(config_class=Config):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates",
    )
    app.config.from_object(config_class)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///instance/"):
        db_name = uri.replace("sqlite:///instance/", "")
        db_path = Path(app.instance_path) / db_name
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path.resolve().as_posix()

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app import models  # noqa: F401
    from app.blueprints.admin import admin_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.cases import cases_bp
    from app.blueprints.catalog import catalog_bp
    from app.blueprints.main import main_bp
    from app.blueprints.news import news_bp
    from app.blueprints.pages import pages_bp
    from app.errors import errors_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(errors_bp)

    from app.cli import register_cli

    register_cli(app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == "admin":
            return AdminUser()
        return None

    @app.template_filter("media")
    def media_url(path):
        if not path:
            return ""
        text = str(path)
        if text.startswith(("http://", "https://", "/")):
            return text
        return "/static/" + text.lstrip("/")

    @app.template_filter("rub")
    def rub_format(value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return value
        return f"{number:,.0f}".replace(",", " ")

    @app.context_processor
    def inject_globals():
        from app.models import ProductCategory

        cart = CartService()
        return {
            "csrf_token": generate_csrf,
            "current_user": current_user,
            "get_setting": get_setting,
            "render_markdown": render_markdown,
            "cart_count": cart.count(),
            "nav_categories": ProductCategory.query.order_by(ProductCategory.sort_order, ProductCategory.id).all(),
            "phone": get_setting("header.phone", "+7 (909) 112-52-05"),
            "address": get_setting("header.address", "Агатовая улица, 28, Пермь"),
            "hours": get_setting("header.hours", "7 дней в неделю: 09:00–20:00"),
            "email": get_setting("contacts.email", "vip.shapen@mail.ru"),
        }

    return app
