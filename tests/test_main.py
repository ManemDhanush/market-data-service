import pytest
from app.api.main import app
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.core.db import Base, engine

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)


def test_calculate_moving_average():
    prices = [100, 101, 99, 102, 98]
    expected = 100
    result = round(sum(prices) / len(prices), 2)
    assert result == expected


def test_get_latest_price():
    response = client.get("/prices/latest?symbol=AAPL")
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert isinstance(body["price"], float)
    assert "timestamp" in body
    assert body["provider"] == "yfinance"


def test_get_moving_average():
    response = client.get("/moving-average?symbol=AAPL")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        body = response.json()
        assert body["symbol"] == "AAPL"
        assert "moving_average" in body


def test_get_price_history():
    response = client.get("/prices/history?symbol=AAPL")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        body = response.json()
        assert isinstance(body, list)
        assert "price" in body[0]


def test_get_latest_price_success():
    response = client.get("/prices/latest?symbol=AAPL")
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert isinstance(body["price"], float)
    assert "timestamp" in body
    assert body["provider"] == "yfinance"


def test_get_latest_price_invalid_symbol():
    response = client.get("/prices/latest?symbol=INVALIDSYMBOL123")
    assert response.status_code in (404, 500)


@patch("app.api.main.publish_price_event")
def test_poll_prices_success(mock_publish):
    payload = {
        "symbols": ["AAPL", "MSFT"],
        "interval": 60,
        "provider": "yfinance"
    }
    response = client.post("/prices/poll", json=payload)
    assert response.status_code == 202
    body = response.json()
    assert "job_id" in body
    assert body["status"] == "accepted"
    assert body["config"]["symbols"] == ["AAPL", "MSFT"]
    assert mock_publish.call_count == 2


def test_poll_prices_empty_symbols():
    payload = {
        "symbols": [],
        "interval": 60,
        "provider": "yfinance"
    }
    response = client.post("/prices/poll", json=payload)
    assert response.status_code == 422


def test_get_price_history_no_data():
    response = client.get("/prices/history?symbol=ZZZZ")
    assert response.status_code == 404
    assert response.json()["detail"] == "No price history found"


def test_get_moving_average_not_found():
    response = client.get("/moving-average?symbol=ZZZZ")
    assert response.status_code == 404
    assert response.json()["detail"] == "No moving average found"
