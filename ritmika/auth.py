"""Авторизация: регистрация, вход, выход, кабинет и админ-панель."""

from __future__ import annotations

import re

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db, query_all, query_one

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PASSWORD_MIN = 8

bp = Blueprint("auth", __name__)


def current_user() -> dict | None:
    """Данные вошедшего пользователя или None."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    row = query_one("SELECT id, email, is_admin FROM users WHERE id = ?", (user_id,))
    return dict(row) if row else None


def is_admin() -> bool:
    """Флаг администратора из базы (не из сессии)."""
    user = current_user()
    return bool(user and user["is_admin"])


def create_admin(email: str, pwd: str) -> int:
    """Создаёт администратора (используется CLI-командой)."""
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise ValueError("Некорректный email администратора")
    if len(pwd) < PASSWORD_MIN:
        raise ValueError(f"Пароль короче {PASSWORD_MIN} символов")
    db = get_db()
    cursor = db.execute(
        "INSERT INTO users (email, password_hash, is_admin) VALUES (?, ?, 1)",
        (email, generate_password_hash(pwd)),
    )
    db.commit()
    return cursor.lastrowid


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Регистрация нового покупателя."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        form_password = request.form.get("password", "")
        if not EMAIL_RE.match(email):
            flash("Проверьте email — кажется, в нём опечатка.", "error")
        elif len(form_password) < PASSWORD_MIN:
            flash(f"Пароль должен быть не короче {PASSWORD_MIN} символов.", "error")
        elif query_one("SELECT id FROM users WHERE email = ?", (email,)) is not None:
            flash("Такой email уже зарегистрирован — войдите вместо регистрации.", "error")
        else:
            db = get_db()
            cursor = db.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, generate_password_hash(form_password)),
            )
            db.commit()
            session["user_id"] = cursor.lastrowid
            flash("Аккаунт создан. Добро пожаловать в Ritmika!")
            return redirect(url_for("shop.index"))
    return render_template("auth_form.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Вход по email и паролю."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        form_password = request.form.get("password", "")
        row = query_one("SELECT * FROM users WHERE email = ?", (email,))
        if row is None or not check_password_hash(row["password_hash"], form_password):
            flash("Email или пароль неверны.", "error")
        else:
            session["user_id"] = row["id"]
            flash("С возвращением!")
            return redirect(url_for("shop.index"))
    return render_template("auth_form.html")


@bp.route("/logout", methods=["POST"])
def logout():
    """Выход — только POST, чтобы ссылка не выходила сама."""
    session.pop("user_id", None)
    flash("Вы вышли из аккаунта.")
    return redirect(url_for("shop.index"))


@bp.route("/me")
def profile():
    """Личный кабинет: заказы вошедшего пользователя."""
    user = current_user()
    if user is None:
        abort(403)
    orders = query_all(
        "SELECT id, total, created_at FROM orders WHERE user_id = ? ORDER BY id DESC",
        (user["id"],),
    )
    items: dict[int, list] = {}
    for order in orders:
        items[order["id"]] = query_all(
            "SELECT name, size, qty, price FROM order_items WHERE order_id = ?",
            (order["id"],),
        )
    return render_template("orders.html", user=user, orders=orders, items=items)


@bp.route("/admin")
def admin():
    """Админ-панель: все заказы магазина."""
    if not is_admin():
        abort(403)
    orders = query_all(
        "SELECT id, user_id, name, email, total, created_at"
        " FROM orders ORDER BY id DESC LIMIT 200"
    )
    return render_template("admin.html", orders=orders)
