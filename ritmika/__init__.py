"""Фабрика приложения Ritmika."""

from __future__ import annotations

import secrets
from pathlib import Path

import click
from flask import Flask, abort, request, session

from . import db


def _instance_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "instance"


def _load_secret() -> str:
    """Секретный ключ сессий: создаётся один раз и хранится вне git."""
    directory = _instance_dir()
    directory.mkdir(parents=True, exist_ok=True)
    secret_file = directory / "secret_key"
    if secret_file.exists():
        return secret_file.read_text(encoding="utf-8")
    key = secrets.token_hex(32)
    secret_file.write_text(key, encoding="utf-8")
    return key


def create_app(test_config: dict | None = None) -> Flask:
    """Создаёт и настраивает приложение Ritmika."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="test" if test_config else _load_secret(),
        DATABASE=str(_instance_dir() / "ritmika.db"),
    )
    if test_config:
        app.config.update(test_config)

    db.init_db(app.config["DATABASE"])
    app.teardown_appcontext(db.close_db)

    from . import auth, shop

    app.register_blueprint(auth.bp)
    app.register_blueprint(shop.bp)

    @app.before_request
    def csrf_protect() -> None:
        """CSRF: токен живёт в сессии и сверяется на каждом POST."""
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_hex(16)
        if request.method == "POST" and request.form.get("_csrf") != session["_csrf"]:
            abort(400, description="Недействительный CSRF-токен")

    @app.context_processor
    def inject_globals() -> dict:
        from .auth import current_user
        from .shop import cart_count

        return {
            "csrf_token": session.get("_csrf", ""),
            "cart_count": cart_count(),
            "user": current_user(),
        }

    @app.template_filter("price_fmt")
    def price_fmt(value: int) -> str:
        """24900 → '24 900 ₽'."""
        return f"{value:,}".replace(",", "\u00A0") + " ₽"

    @app.cli.command("create-admin")
    @click.argument("email")
    @click.argument("password")
    def create_admin_command(email: str, password: str) -> None:
        """Создаёт администратора: flask --app run.py create-admin EMAIL PASSWORD."""
        from .auth import create_admin

        create_admin(email, password)
        click.echo(f"Администратор {email} создан.")

    return app
