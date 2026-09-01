from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.models import Transaction, User


class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, user_id: int, payload: dict) -> Transaction:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        transaction = Transaction(
            user_id=user_id,
            amount=float(payload["amount"]),
            currency=str(payload.get("currency", "USD")).upper(),
            merchant=str(payload["merchant"]).strip(),
            description=str(payload.get("description", "")),
            transaction_date=payload.get("transaction_date") or datetime.utcnow(),
            category=str(payload.get("category") or "uncategorized"),
            confidence_score=float(payload.get("confidence_score", 0.0)),
            source=str(payload.get("source", "manual")),
            created_at=datetime.utcnow(),
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def list_transactions(self, user_id: int, category: Optional[str] = None, merchant: Optional[str] = None) -> List[Transaction]:
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        if category:
            query = query.filter(Transaction.category == category)
        if merchant:
            query = query.filter(Transaction.merchant.ilike(f"%{merchant}%"))
        return query.order_by(Transaction.transaction_date.desc()).all()

    def get_transaction(self, user_id: int, transaction_id: int) -> Transaction:
        transaction = (
            self.db.query(Transaction)
            .filter(Transaction.user_id == user_id, Transaction.id == transaction_id)
            .first()
        )
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return transaction
