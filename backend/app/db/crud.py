from sqlalchemy import func
from app.db.session import SessionLocal
from app.db.models import Expense, Budget


# -------------------------
# CREATE EXPENSE
# -------------------------
def create_expense(
    file_id: str,
    date: str | None,
    merchant: str | None,
    amount: float | None,
    category: str,
    payment_mode: str | None = None,
):
    db = SessionLocal()

    exp = Expense(
        file_id=file_id,
        date=date,
        merchant=merchant,
        amount=amount,
        category=category,
        payment_mode=payment_mode,
    )

    db.add(exp)
    db.commit()
    db.refresh(exp)
    db.close()
    return exp


# -------------------------
# BASIC ANALYTICS
# -------------------------
def get_category_totals():
    db = SessionLocal()
    results = (
        db.query(Expense.category, func.sum(Expense.amount).label("total"))
        .group_by(Expense.category)
        .all()
    )
    db.close()
    return [{"category": r.category, "total": float(r.total or 0)} for r in results]


# -------------------------
# MONTHLY ANALYTICS
# -------------------------
def get_monthly_totals():
    db = SessionLocal()
    results = (
        db.query(
            func.substr(Expense.date, 1, 7).label("month"),
            func.sum(Expense.amount).label("total")
        )
        .filter(Expense.date.isnot(None))
        .group_by("month")
        .order_by("month")
        .all()
    )
    db.close()
    return [{"month": r.month, "total": float(r.total or 0)} for r in results]


def get_monthly_category_totals():
    db = SessionLocal()
    results = (
        db.query(
            func.substr(Expense.date, 1, 7).label("month"),
            Expense.category.label("category"),
            func.sum(Expense.amount).label("total")
        )
        .filter(Expense.date.isnot(None))
        .group_by("month", "category")
        .order_by("month", "category")
        .all()
    )
    db.close()
    return [{"month": r.month, "category": r.category, "total": float(r.total or 0)} for r in results]


# -------------------------
# BUDGET CRUD
# -------------------------
def set_budget(category: str, monthly_limit: float):
    db = SessionLocal()

    b = db.query(Budget).filter(Budget.category == category).first()
    if b:
        b.monthly_limit = monthly_limit
    else:
        b = Budget(category=category, monthly_limit=monthly_limit)
        db.add(b)

    db.commit()
    db.refresh(b)
    db.close()
    return b


def get_all_budgets():
    db = SessionLocal()
    rows = db.query(Budget).all()
    db.close()
    return [{"category": r.category, "monthly_limit": float(r.monthly_limit)} for r in rows]


def check_budget_overruns(month: str):
    db = SessionLocal()

    spend = (
        db.query(Expense.category, func.sum(Expense.amount).label("total"))
        .filter(Expense.date.like(f"{month}-%"))
        .group_by(Expense.category)
        .all()
    )

    budgets = {b.category: b.monthly_limit for b in db.query(Budget).all()}
    db.close()

    alerts = []
    for s in spend:
        cat = s.category
        total = float(s.total or 0)
        limit = float(budgets.get(cat, 0))

        if limit > 0 and total > limit:
            alerts.append({
                "category": cat,
                "spent": total,
                "budget": limit,
                "overshoot": round(total - limit, 2)
            })

    return alerts


# -------------------------
# WEEKLY / RANGE REPORTS
# -------------------------
def get_range_total(start_date: str, end_date: str) -> float:
    db = SessionLocal()
    total = (
        db.query(func.sum(Expense.amount))
        .filter(Expense.date >= start_date, Expense.date <= end_date)
        .scalar()
    )
    db.close()
    return float(total or 0)


def get_range_category_totals(start_date: str, end_date: str):
    db = SessionLocal()
    rows = (
        db.query(Expense.category, func.sum(Expense.amount).label("total"))
        .filter(Expense.date >= start_date, Expense.date <= end_date)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )
    db.close()
    return [{"category": r.category, "total": float(r.total or 0)} for r in rows]


def get_range_payment_totals(start_date: str, end_date: str):
    db = SessionLocal()
    rows = (
        db.query(Expense.payment_mode, func.sum(Expense.amount).label("total"))
        .filter(Expense.date >= start_date, Expense.date <= end_date)
        .group_by(Expense.payment_mode)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )
    db.close()
    return [{"payment_mode": (r.payment_mode or "UNKNOWN"), "total": float(r.total or 0)} for r in rows]


def get_range_top_merchants(start_date: str, end_date: str, limit: int = 5):
    db = SessionLocal()
    rows = (
        db.query(Expense.merchant, func.sum(Expense.amount).label("total"))
        .filter(Expense.date >= start_date, Expense.date <= end_date)
        .group_by(Expense.merchant)
        .order_by(func.sum(Expense.amount).desc())
        .limit(limit)
        .all()
    )
    db.close()
    return [{"merchant": (r.merchant or "UNKNOWN"), "total": float(r.total or 0)} for r in rows]