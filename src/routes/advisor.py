from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.schemas import AdviceResponse, AdvisorQuery
from src.services.ai_service import AIExpenseService
from src.services.budget_service import BudgetService
from src.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/v1", tags=["advisor"])


@router.post("/advisor", response_model=AdviceResponse)
def ask_advisor(payload: AdvisorQuery, db: Session = Depends(get_db)):
    service = AIExpenseService()
    tx_service = TransactionService(db)
    budget_service = BudgetService(db)

    user_transactions = tx_service.list_transactions(user_id=1)
    budget_status = budget_service.get_budget_status(user_id=1, budget_id=1) if budget_service.list_budgets(user_id=1) else {"status": "no_budget"}

    recent_context = "User has spent " + str(sum(t.amount for t in user_transactions)) + " across recent transactions."
    if isinstance(budget_status, dict):
        recent_context += f" Current budget status: {budget_status.get('status', 'unknown')}."

    docs = [
        "Create a monthly spending plan by grouping recurring categories.",
        "Reduce discretionary spending when monthly limits are exceeded.",
        "Use automated alerts to catch overspending before it compounds.",
    ]

    result = service.generate_advice(payload.question, recent_context, docs)
    return AdviceResponse(**result)
