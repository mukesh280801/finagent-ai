from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

Base = declarative_base()

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, nullable=False)
    date = Column(String, nullable=True)
    merchant = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    category = Column(String, nullable=False, default="misc")
    payment_mode = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, nullable=False)
    monthly_limit = Column(Float, nullable=False)