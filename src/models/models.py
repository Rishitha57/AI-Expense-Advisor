from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    alerts = relationship("AlertLog", back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    merchant = Column(String(255), nullable=False)
    description = Column(Text, default="")
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    category = Column(String(100), default="uncategorized")
    confidence_score = Column(Float, default=0.0)
    source = Column(String(100), default="manual")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(100), nullable=False, default="overall")
    monthly_limit = Column(Float, nullable=False)
    alert_threshold = Column(Float, default=0.8)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="budgets")


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=True)
    alert_type = Column(String(100), default="budget")
    trigger_value = Column(Float, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(255), default="finance")
    source = Column(String(255), default="internal")
    version = Column(String(50), default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
