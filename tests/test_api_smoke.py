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


def test_rejects_malformed_transaction_payload():
    client = TestClient(app)
    payload = {
        "currency": "USD",
        "merchant": "Missing Amount Cafe",
        "transaction_date": "2026-08-31T12:00:00Z",
    }

    response = client.post("/api/v1/transactions", json=payload)

    assert response.status_code in {400, 422}, response.text
    assert response.json().get("detail")


def test_returns_not_found_for_missing_transaction():
    client = TestClient(app)

    response = client.get("/api/v1/transactions/999999999")

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Transaction not found"


def test_handles_invalid_query_and_path_parameters():
    client = TestClient(app)

    unsupported_query_response = client.get(
        "/api/v1/transactions",
        params={"limit": "not-a-number"},
    )
    invalid_id_response = client.get("/api/v1/transactions/not-an-integer")

    assert unsupported_query_response.status_code == 200, unsupported_query_response.text
    assert isinstance(unsupported_query_response.json(), list)
    assert invalid_id_response.status_code == 422, invalid_id_response.text
    assert invalid_id_response.json().get("detail")
