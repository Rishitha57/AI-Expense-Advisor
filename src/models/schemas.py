from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    merchant: str = Field(..., min_length=1)
    description: str = ""
    transaction_date: datetime
    source: str = "manual"
    category: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category: str
    confidence_score: float = 0.0
    created_at: datetime


class BudgetBase(BaseModel):
    category: str = "overall"
    monthly_limit: float = Field(..., gt=0)
    alert_threshold: float = Field(0.8, ge=0, le=1)


class BudgetCreate(BudgetBase):
    pass


class BudgetRead(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    budget_id: Optional[int] = None
    alert_type: str
    trigger_value: float
    message: str
    created_at: datetime


class BudgetStatus(BaseModel):
    budget_id: int
    category: str
    monthly_limit: float
    alert_threshold: float
    spent: float
    remaining: float
    status: str
    triggered: bool


class AdvisorQuery(BaseModel):
    question: str = Field(..., min_length=1)


class AdviceResponse(BaseModel):
    question: str
    answer: str
    evidence: list[str]
    context_summary: str


class KnowledgeArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    tags: str
    source: str
    version: str
    created_at: datetime
