from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.schemas import TransactionCreate, TransactionRead
from src.services.ai_service import AIExpenseService
from src.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/v1", tags=["transactions"])


@router.post("/transactions", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
):
    service = TransactionService(db)
    user_id = 1
    category, confidence = AIExpenseService().classify_transaction(payload.merchant, payload.description)
    data = payload.model_dump()
    data["category"] = category
    data["confidence_score"] = confidence
    transaction = service.create_transaction(user_id, data)
    return transaction


@router.get("/transactions", response_model=list[TransactionRead])
def list_transactions(
    category: Optional[str] = Query(None),
    merchant: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    service = TransactionService(db)
    user_id = 1
    return service.list_transactions(user_id=user_id, category=category, merchant=merchant)


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    service = TransactionService(db)
    user_id = 1
    return service.get_transaction(user_id=user_id, transaction_id=transaction_id)
