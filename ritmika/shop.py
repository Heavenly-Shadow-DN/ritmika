"""Магазин: главная, каталог, товар, серверная корзина, заказ и подписка."""

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

from .auth import current_user
from .db import get_db, query_one
from .products import (
    CATEGORIES,
    CATEGORY_TITLES,
    PRODUCTS,
    get_product,
    products_by_cat,
    similar_to,
    size_is_valid,
)

bp = Blueprint("shop", __name__)

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_RE = re.compile(r"^\+?[\d\s()-]{10,}$")
FREE_DELIVERY_FROM = 10000
DELIVERY_PRICE = 400
MAX_QTY = 99


# ---------- Корзина в сессии ----------


def _cart() -> dict[str, int]:
    """Корзина сессии: ключ '{id}__{size}' → количество."""
    return session.setdefault("cart", {})


def cart_count() -> int:
    """Сколько единиц товара в корзине (для бейджа)."""
    return sum(_cart().values())


def cart_details() -> list[dict]:
    """Строки корзины, соединённые с данными товаров; цена берётся с сервера."""
    rows = []
    for key, qty in _cart().items():
        product_id, _, size = key.partition("__")
        product = get_product(product_id)
        if product is None:
            continue
        rows.append(
            {
                "key": key,
                "product": product,
                "size": size,
                "qty": qty,
                "sum": product.price * qty,
            }
        )
    return rows


def cart_totals() -> dict[str, int]:
    """Итоги корзины: сумма, доставка, всего."""
    items_total = sum(row["sum"] for row in cart_details())
    count = cart_count()
    delivery = 0 if count == 0 or items_total >= FREE_DELIVERY_FROM else DELIVERY_PRICE
    return {
        "count": count,
        "items_total": items_total,
        "delivery": delivery,
        "total": items_total + delivery,
    }


def _safe_next(default: str) -> str:
    """Защита от open redirect: принимаем только пути внутри сайта."""
    candidate = request.form.get("next", "")
    if candidate.startswith("/") and not candidate.startswith("//"):
        return candidate
    return default


# ---------- Страницы ----------


@bp.route("/")
def index():
    """Главная: новинки и лукбук."""
    return render_template("index.html", newin=PRODUCTS[:4])


@bp.route("/catalog")
def catalog():
    """Каталог с серверной фильтрацией и сортировкой."""
    cat = request.args.get("cat", "all")
    sort = request.args.get("sort", "default")
    if cat not in {"all", "outer", "knit", "pants", "shirt", "dress", "acc"}:
        cat = "all"
    if sort not in {"default", "asc", "desc"}:
        sort = "default"

    items = products_by_cat(cat)
    if sort == "asc":
        items = sorted(items, key=lambda p: p.price)
    elif sort == "desc":
        items = sorted(items, key=lambda p: p.price, reverse=True)

    return render_template(
        "catalog.html",
        items=items,
        cat=cat,
        sort=sort,
        categories=CATEGORIES,
        cat_title=CATEGORY_TITLES.get(cat, cat),
    )


@bp.route("/product/<product_id>")
def product(product_id: str):
    """Карточка товара."""
    item = get_product(product_id)
    if item is None:
        abort(404)
    return render_template("product.html", item=item, similar=similar_to(item))


# ---------- Корзина и заказ ----------


@bp.route("/cart")
def cart():
    """Корзина с формой оформления."""
    return render_template(
        "cart.html",
        rows=cart_details(),
        totals=cart_totals(),
        defaults={"name": "", "phone": "", "email": "", "address": ""},
    )


@bp.route("/cart/add", methods=["POST"])
def cart_add():
    """Добавление товара: размер проверяется по данным товара."""
    item = get_product(request.form.get("product_id", ""))
    size = request.form.get("size", "")
    if item is None or not size_is_valid(item, size):
        abort(400)
    key = f"{item.id}__{size}"
    cart = _cart()
    cart[key] = min(cart.get(key, 0) + 1, MAX_QTY)
    session.modified = True
    flash(f"{item.name} — в корзине (размер {size}).")
    return redirect(_safe_next(url_for("shop.product", product_id=item.id)))


@bp.route("/cart/update", methods=["POST"])
def cart_update():
    """Изменение количества позиции."""
    key = request.form.get("key", "")
    if key not in _cart():
        abort(400)
    try:
        qty = int(request.form.get("qty", "1"))
    except ValueError:
        abort(400)
    cart = _cart()
    if qty <= 0:
        del cart[key]
    else:
        cart[key] = min(qty, MAX_QTY)
    session.modified = True
    return redirect(url_for("shop.cart"))


@bp.route("/cart/remove", methods=["POST"])
def cart_remove():
    """Удаление позиции из корзины."""
    key = request.form.get("key", "")
    cart = _cart()
    if key not in cart:
        abort(400)
    del cart[key]
    session.modified = True
    return redirect(url_for("shop.cart"))


@bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    """Оформление заказа: валидация на сервере, запись в БД."""
    totals = cart_totals()
    if totals["count"] == 0:
        flash("Корзина пуста — сначала выберите вещи.")
        return redirect(url_for("shop.catalog"))

    user = current_user()
    defaults = {
        "name": request.form.get("name", ""),
        "phone": request.form.get("phone", ""),
        "email": request.form.get("email", "") or (user["email"] if user else ""),
        "address": request.form.get("address", ""),
    }

    if request.method == "POST":
        if not re.match(r"^.{2,}$", defaults["name"].strip()):
            flash("Укажите имя и фамилию — так к вам обратится курьер.", "error")
        elif not PHONE_RE.match(defaults["phone"].strip()):
            flash("Проверьте телефон: нужны все цифры.", "error")
        elif not EMAIL_RE.match(defaults["email"].strip()):
            flash("Похоже, в почте опечатка.", "error")
        elif len(defaults["address"].strip()) < 5:
            flash("Укажите адрес доставки подробнее.", "error")
        elif request.form.get("consent") != "on":
            flash("Нужно согласие на обработку персональных данных.", "error")
        else:
            order_id = _create_order(defaults, user["id"] if user else None)
            session.pop("cart", None)
            session["last_order"] = order_id
            return redirect(url_for("shop.order", order_id=order_id))

    return render_template(
        "cart.html",
        rows=cart_details(),
        totals=totals,
        show_checkout=True,
        defaults=defaults,
    )


def _create_order(defaults: dict[str, str], user_id: int | None) -> int:
    """Сохраняет заказ и позиции; цены берутся из данных, не из формы."""
    totals = cart_totals()
    db = get_db()
    cursor = db.execute(
        "INSERT INTO orders (user_id, name, phone, email, address, items_total,"
        " delivery, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            user_id,
            defaults["name"].strip(),
            defaults["phone"].strip(),
            defaults["email"].strip(),
            defaults["address"].strip(),
            totals["items_total"],
            totals["delivery"],
            totals["total"],
        ),
    )
    order_id = int(cursor.lastrowid)
    for row in cart_details():
        db.execute(
            "INSERT INTO order_items (order_id, product_id, name, size, qty, price)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                order_id,
                row["product"].id,
                row["product"].name,
                row["size"],
                row["qty"],
                row["product"].price,
            ),
        )
    db.commit()
    return order_id


@bp.route("/order/<int:order_id>")
def order(order_id: int):
    """Подтверждение заказа: виден автору сессии или владельцу."""
    if session.get("last_order") != order_id:
        user = current_user()
        row = query_one("SELECT user_id FROM orders WHERE id = ?", (order_id,))
        if row is None or row["user_id"] is None or user is None or user["id"] != row["user_id"]:
            abort(403)
    order_row = query_one("SELECT * FROM orders WHERE id = ?", (order_id,))
    if order_row is None:
        abort(404)
    items = get_db().execute(
        "SELECT name, size, qty, price FROM order_items WHERE order_id = ?", (order_id,)
    ).fetchall()
    return render_template("order.html", order=order_row, items=items)


# ---------- Подписка ----------


@bp.route("/subscribe", methods=["POST"])
def subscribe():
    """Подписка на рассылку с согласием по 152-ФЗ."""
    email = request.form.get("email", "").strip().lower()
    if not EMAIL_RE.match(email):
        flash("Похоже, в адресе опечатка — проверьте почту.", "error")
        return redirect(request.referrer or url_for("shop.index"))
    if request.form.get("consent") != "on":
        flash("Нужно согласие на обработку персональных данных.", "error")
        return redirect(request.referrer or url_for("shop.index"))
    db = get_db()
    existing = query_one("SELECT id FROM subscribers WHERE email = ?", (email,))
    if existing is None:
        db.execute("INSERT INTO subscribers (email) VALUES (?)", (email,))
        db.commit()
        flash("Готово! Первое письмо придёт в начале месяца.")
    else:
        flash("Этот email уже в списке рассылки.")
    return redirect(request.referrer or url_for("shop.index"))


# ---------- Статические страницы ----------


@bp.route("/lookbook")
def lookbook():
    return render_template("lookbook.html")


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/legal")
def legal():
    return render_template("legal.html")
