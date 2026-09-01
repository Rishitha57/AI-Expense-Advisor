from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.schemas import BudgetCreate, BudgetRead, BudgetStatus
from src.services.budget_service import BudgetService

router = APIRouter(prefix="/api/v1", tags=["budgets"])


@router.post("/budgets", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    service = BudgetService(db)
    budget = service.create_budget(user_id=1, payload=payload.model_dump())
    return budget


@router.get("/budgets", response_model=List[BudgetRead])
def list_budgets(db: Session = Depends(get_db)):
    service = BudgetService(db)
    return service.list_budgets(user_id=1)


@router.get("/budgets/{budget_id}/status", response_model=BudgetStatus)
def get_budget_status(budget_id: int, db: Session = Depends(get_db)):
    service = BudgetService(db)
    return service.get_budget_status(user_id=1, budget_id=budget_id)
