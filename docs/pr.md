# AI Expense Advisor — Pull Request

## 1. Summary
This PR delivers the initial backend implementation for the AI Expense Advisor capstone project. The application introduces a FastAPI-based service for transaction ingestion, budget tracking, and AI-assisted financial guidance. It establishes the project foundation for the core user stories defined in the requirements and architecture documents:

- US-001: Automated Transaction Ingestion & Categorization
- US-002: Personalized Budget Alerts & RAG Advisor

The current implementation provides the first working backend scaffold with persistence, domain models, service patterns, and route handlers for the main expenditure flows. It also includes a real live API smoke test confirming the transaction flow works end-to-end.

---

## 2. Changes Made
- Created the FastAPI application entrypoint in [main.py](../main.py)
- Added SQLAlchemy database configuration and schema setup in [src/models/database.py](../src/models/database.py) and [src/models/models.py](../src/models/models.py)
- Added Pydantic schemas for transactions, budgets, and advisor responses in [src/models/schemas.py](../src/models/schemas.py)
- Implemented domain logic for transaction ingestion and listing in [src/services/transaction_service.py](../src/services/transaction_service.py)
- Implemented budget calculation and alert support in [src/services/budget_service.py](../src/services/budget_service.py)
- Added AI classification and advisory logic in [src/services/ai_service.py](../src/services/ai_service.py)
- Exposed API routes for transactions, budgets, and advisor requests in:
  - [src/routes/transactions.py](../src/routes/transactions.py)
  - [src/routes/budgets.py](../src/routes/budgets.py)
  - [src/routes/advisor.py](../src/routes/advisor.py)
- Added startup initialization to create the SQLite schema and seed a demo user
- Added smoke-test fixtures and validation scripts in:
  - [tests/sample_transactions.json](../tests/sample_transactions.json)
  - [tests/test_api_smoke.py](../tests/test_api_smoke.py)

---

## 3. Test Evidence
The key live smoke test was executed against the running FastAPI app at http://127.0.0.1:8000.

### API Smoke Test Result
We posted a sample transaction to the live endpoint:
- POST /api/v1/transactions
- Request payload includes amount, merchant, currency, description, and timestamp

Observed response from the running service:
- `merchant: Whole Foods`
- `currency: USD`
- `category: uncategorized`
- `id: 1`
- `user_id: 1`
- `confidence_score: 0.4`

Immediately after the POST, a GET to /api/v1/transactions returned the same transaction record, confirming that the transaction was persisted and retrievable through the API.

This result was validated using the smoke test script in [tests/test_api_smoke.py](../tests/test_api_smoke.py), which exercises the live endpoint and prints the POST and GET status/results.

---

## 4. Error Handling & Robustness Validation
The API smoke-test suite includes dedicated negative cases alongside the positive transaction ingestion flow:
- Malformed transaction payloads with missing required fields return a structured `422` or `400` validation response.
- Requests for non-existent transactions return `404 Not Found` with the expected `Transaction not found` detail.
- Invalid transaction identifiers return `422`, and unsupported query parameters are handled gracefully without a server error.

The tests were executed with verbose pytest reporting so positive and negative outcomes are collected and visible as separate test results. This validates predictable API behavior for malformed input, missing resources, and common request-boundary errors.

---

## 5. Known Limitations
- The application currently uses SQLite for local development, not PostgreSQL as described in the target architecture.
- Authentication and user-level authorization are not yet fully hardened or production-ready.
- GDPR/privacy handling and data retention controls are still pending the security/compliance follow-up noted in the design review.
- Budget alerts and RAG advisor logic are scaffolded but not yet fully production-hardened for real-world financial guidance generation.
- AI classification is intentionally lightweight and deterministic; it is not yet a full production model pipeline.
- The project is an MVP backend foundation and should be treated as an initial working implementation rather than final production deployment code.

---

## 6. Reviewer Checklist
- [ ] The application architecture matches the intended capstone scope and MVP direction.
- [ ] Transaction ingestion endpoint is functioning and persisting data correctly.
- [ ] API behavior is validated by the live smoke test evidence.
- [ ] Budget and advisor routes are present and aligned with the design goals.
- [ ] Security/privacy concerns from the design review have been acknowledged and tracked.
- [ ] Remaining limitations are clearly understood before moving to the next release stage.
- [ ] The code is suitable for review, refinement, and subsequent enhancement in the next iteration.
