import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient

from main import app


def test_post_and_get_transactions():
    client = TestClient(app)

    payload = {
        "amount": 45.75,
        "currency": "USD",
        "merchant": "Whole Foods",
        "description": "Groceries",
        "transaction_date": "2026-08-31T12:00:00Z",
    }

    create_response = client.post("/api/v1/transactions", json=payload)
    assert create_response.status_code == 201, create_response.text

    created = create_response.json()
    assert created["merchant"] == payload["merchant"]
    assert created["amount"] == payload["amount"]
    assert created["currency"] == payload["currency"]

    list_response = client.get("/api/v1/transactions")
    assert list_response.status_code == 200, list_response.text

    transactions = list_response.json()
    assert isinstance(transactions, list)
    assert any(
        item["merchant"] == payload["merchant"] and float(item["amount"]) == payload["amount"]
        for item in transactions
    )


def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ok"
