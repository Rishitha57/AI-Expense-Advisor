from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.models import AlertLog, Budget, Transaction, User


class BudgetService:
    def __init__(self, db: Session):
        self.db = db

    def create_budget(self, user_id: int, payload: dict) -> Budget:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        budget = Budget(
            user_id=user_id,
            category=str(payload.get("category", "overall")),
            monthly_limit=float(payload["monthly_limit"]),
            alert_threshold=float(payload.get("alert_threshold", 0.8)),
            created_at=datetime.utcnow(),
        )

        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def list_budgets(self, user_id: int) -> List[Budget]:
        return self.db.query(Budget).filter(Budget.user_id == user_id).all()

    def get_budget_status(self, user_id: int, budget_id: int) -> dict:
        budget = self.db.query(Budget).filter(Budget.user_id == user_id, Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year

        spent = (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.category == budget.category,
                Transaction.transaction_date >= datetime(current_year, current_month, 1),
            )
            .with_entities(__import__("sqlalchemy").func.coalesce(__import__("sqlalchemy").func.sum(Transaction.amount), 0.0))
            .scalar()
        )

        spent = float(spent or 0.0)
        remaining = budget.monthly_limit - spent
        threshold_value = budget.monthly_limit * float(budget.alert_threshold)
        triggered = spent >= threshold_value

        return {
            "budget_id": budget.id,
            "category": budget.category,
            "monthly_limit": budget.monthly_limit,
            "alert_threshold": budget.alert_threshold,
            "spent": spent,
            "remaining": remaining,
            "status": "warning" if triggered else "ok",
            "triggered": triggered,
        }

    def create_alert(self, user_id: int, budget_id: int, message: str, trigger_value: float) -> AlertLog:
        alert = AlertLog(
            user_id=user_id,
            budget_id=budget_id,
            alert_type="budget",
            trigger_value=trigger_value,
            message=message,
            created_at=datetime.utcnow(),
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert
