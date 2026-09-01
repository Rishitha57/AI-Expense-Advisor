from src.routes.transactions import router as transactions_router
from src.routes.budgets import router as budgets_router
from src.routes.advisor import router as advisor_router

__all__ = ["transactions_router", "budgets_router", "advisor_router"]
