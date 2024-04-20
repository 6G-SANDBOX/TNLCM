import pytest

from app import app

@pytest.fixture
def test_app():
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "Test_key",
    })
    return app

@pytest.fixture
def client(test_app):
    return test_app.test_client()

@pytest.fixture
def runner(test_app):
    return test_app.test_cli_runner()