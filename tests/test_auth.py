"""Тесты авторизации: регистрация, вход, кабинет, админ-панель."""


def _register(client, csrf, email="user@example.ru", password="password123"):
    return client.post("/register", data={"_csrf": csrf, "email": email, "password": password})


def test_register_and_login_session(client, csrf):
    assert _register(client, csrf).status_code == 302
    assert "Кабинет" in client.get("/").text


def test_register_short_password(client, csrf):
    rv = _register(client, csrf, email="x@example.ru", password="short")
    assert "не короче" in rv.text


def test_register_bad_email(client, csrf):
    rv = _register(client, csrf, email="not-an-email")
    assert "опечатка" in rv.text


def test_register_duplicate_email(client, csrf):
    _register(client, csrf, email="dup@example.ru")
    client.get("/")  # пересоздаёт CSRF после сброса сессии
    with client.session_transaction() as session:
        fresh_csrf = session["_csrf"]
    rv = _register(client, fresh_csrf, email="dup@example.ru")
    assert "уже зарегистрирован" in rv.text


def test_login_wrong_password(client, csrf):
    _register(client, csrf, email="user@example.ru")
    rv = client.post("/login", data={
        "_csrf": csrf, "email": "user@example.ru", "password": "wrong-password",
    })
    assert "неверны" in rv.text


def test_logout(client, csrf):
    _register(client, csrf)
    client.post("/logout", data={"_csrf": csrf})
    assert client.get("/me").status_code == 403


def test_profile_requires_login(client):
    assert client.get("/me").status_code == 403


def test_admin_requires_admin(client, csrf):
    _register(client, csrf)
    assert client.get("/admin").status_code == 403


def test_admin_ok_for_admin(app, client, csrf):
    _register(client, csrf, email="admin@example.ru")
    with app.app_context():
        from ritmika.db import get_db

        get_db().execute("UPDATE users SET is_admin = 1 WHERE email = 'admin@example.ru'")
        get_db().commit()
    assert client.get("/admin").status_code == 200


def test_order_shows_in_profile(client, csrf):
    _register(client, csrf)
    client.post("/cart/add", data={
        "_csrf": csrf, "product_id": "oktava", "size": "M", "next": "/catalog",
    })
    client.post("/checkout", data={
        "_csrf": csrf, "name": "Анна Ритмова", "phone": "+79000000000",
        "email": "user@example.ru", "address": "Москва, Тверская 1", "consent": "on",
    })
    assert "Заказ №1" in client.get("/me").text


def test_order_linked_to_user(client, csrf):
    _register(client, csrf)
    client.post("/cart/add", data={
        "_csrf": csrf, "product_id": "oktava", "size": "M", "next": "/catalog",
    })
    client.post("/checkout", data={
        "_csrf": csrf, "name": "Анна Ритмова", "phone": "+79000000000",
        "email": "user@example.ru", "address": "Москва, Тверская 1", "consent": "on",
    })
    with client.session_transaction() as session:
        session.clear()
    client.get("/")
    assert client.get("/order/1").status_code == 403
