"""Тесты магазина: страницы, корзина, заказ, подписка, доступ."""

from ritmika.db import query_one


def _add_to_cart(client, csrf, product_id="oktava", size="M"):
    return client.post("/cart/add", data={
        "_csrf": csrf, "product_id": product_id, "size": size, "next": "/catalog",
    })


def test_index_ok(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert "Спокойные вещи" in rv.text


def test_catalog_lists_all_12(client):
    rv = client.get("/catalog")
    assert rv.status_code == 200
    assert rv.text.count("В корзину") == 12


def test_catalog_filter_knit(client):
    rv = client.get("/catalog?cat=knit")
    assert "Свитер «Синкопа»" in rv.text
    assert "Пальто «Октава»" not in rv.text


def test_catalog_unknown_cat_falls_back(client):
    assert client.get("/catalog?cat=../../etc").status_code == 200


def test_catalog_sort_desc(client):
    rv = client.get("/catalog?sort=desc")
    assert rv.text.find("Пальто «Октава»") < rv.text.find("Снуд «Легато»")


def test_product_page_ok(client):
    rv = client.get("/product/oktava")
    assert rv.status_code == 200
    assert "Пальто «Октава»" in rv.text


def test_product_unknown_404(client):
    assert client.get("/product/nope").status_code == 404


def test_post_without_csrf_400(client):
    rv = client.post("/cart/add", data={"product_id": "oktava", "size": "M"})
    assert rv.status_code == 400


def test_add_to_cart(client, csrf):
    rv = _add_to_cart(client, csrf)
    assert rv.status_code == 302
    page = client.get("/cart")
    assert "Пальто «Октава»" in page.text
    assert "24\u00A0900" in page.text


def test_add_invalid_size_400(client, csrf):
    assert client.post("/cart/add", data={
        "_csrf": csrf, "product_id": "oktava", "size": "XXL",
    }).status_code == 400


def test_cart_update_qty(client, csrf):
    _add_to_cart(client, csrf)
    client.post("/cart/update", data={"_csrf": csrf, "key": "oktava__M", "qty": 3})
    assert "74\u00A0700" in client.get("/cart").text


def test_cart_remove(client, csrf):
    _add_to_cart(client, csrf)
    client.post("/cart/remove", data={"_csrf": csrf, "key": "oktava__M"})
    assert "В корзине пока пусто" in client.get("/cart").text


def test_checkout_creates_order(client, csrf):
    _add_to_cart(client, csrf)
    rv = client.post("/checkout", data={
        "_csrf": csrf,
        "name": "Анна Ритмова",
        "phone": "+7 900 000-00-00",
        "email": "anna@example.ru",
        "address": "Москва, Тверская улица, 1",
        "consent": "on",
    })
    assert rv.status_code == 302
    confirmation = client.get(rv.headers["Location"])
    assert "Заказ принят" in confirmation.text
    assert "№1" in confirmation.text
    assert "В корзине пока пусто" in client.get("/cart").text


def test_checkout_persists_items(client, csrf, app):
    _add_to_cart(client, csrf)
    client.post("/checkout", data={
        "_csrf": csrf,
        "name": "Анна Ритмова",
        "phone": "+7 900 000-00-00",
        "email": "anna@example.ru",
        "address": "Москва, Тверская улица, 1",
        "consent": "on",
    })
    with app.app_context():
        row = query_one("SELECT COUNT(*) AS n FROM order_items WHERE product_id = 'oktava'")
        assert row["n"] == 1


def test_checkout_validation(client, csrf):
    _add_to_cart(client, csrf)
    rv = client.post("/checkout", data={
        "_csrf": csrf, "name": "", "phone": "", "email": "", "address": "",
    })
    assert rv.status_code == 200
    assert "Укажите имя" in rv.text


def test_checkout_requires_consent(client, csrf):
    _add_to_cart(client, csrf)
    rv = client.post("/checkout", data={
        "_csrf": csrf, "name": "Анна", "phone": "+79000000000",
        "email": "anna@example.ru", "address": "Москва, Тверская 1",
    })
    assert rv.status_code == 200
    assert "согласие" in rv.text


def test_order_hidden_from_stranger(app, client, csrf):
    _add_to_cart(client, csrf)
    client.post("/checkout", data={
        "_csrf": csrf, "name": "Анна", "phone": "+79000000000",
        "email": "anna@example.ru", "address": "Москва, Тверская 1", "consent": "on",
    })
    stranger = app.test_client()
    assert stranger.get("/order/1").status_code == 403


def test_subscribe_ok(client, csrf):
    rv = client.post("/subscribe", data={
        "_csrf": csrf, "email": "news@example.ru", "consent": "on",
    })
    assert rv.status_code == 302
    page = client.get(rv.headers["Location"])
    assert "Первое письмо" in page.text


def test_subscribe_requires_consent(client, csrf):
    rv = client.post("/subscribe", data={"_csrf": csrf, "email": "news@example.ru"})
    assert "согласие" in client.get(rv.headers["Location"]).text


def test_static_pages_ok(client):
    for path in ("/lookbook", "/about", "/legal"):
        assert client.get(path).status_code == 200
