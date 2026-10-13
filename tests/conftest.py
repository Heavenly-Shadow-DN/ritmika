"""Общие фикстуры для тестов Ritmika."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from ritmika import create_app


@pytest.fixture()
def app(tmp_path):
    """Приложение с временной базой — реальные данные не затрагиваются."""
    return create_app(test_config={
        "DATABASE": str(tmp_path / "test.db"),
        "TESTING": True,
        "SECRET_KEY": "test",
    })


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def csrf(client):
    """CSRF-токен сессии (создаётся при первом GET)."""
    client.get("/")
    with client.session_transaction() as session:
        return session["_csrf"]
