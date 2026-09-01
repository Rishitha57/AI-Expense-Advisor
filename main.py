from fastapi import FastAPI

from src.models.database import Base, SessionLocal, engine
from src.models.models import User
from src.routes.advisor import router as advisor_router
from src.routes.budgets import router as budgets_router
from src.routes.transactions import router as transactions_router

app = FastAPI(title="AI Expense Advisor", version="0.1.0")


def create_db_and_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(email="demo@expense.local", full_name="Demo User", is_active=True))
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    create_db_and_seed()


app.include_router(transactions_router)
app.include_router(budgets_router)
app.include_router(advisor_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
