from datetime import datetime
from app.db.crud import (
    get_monthly_totals,
    get_monthly_category_totals,
    check_budget_overruns,
)

def _to_map(rows, key_fields):
    m = {}
    for r in rows:
        k = tuple(r[f] for f in key_fields)
        m[k] = r
    return m

def generate_monthly_advice(month: str):
    """
    month: 'YYYY-MM'
    Returns insights + alerts + suggestions
    """

    # 1) Monthly totals (overall)
    monthly = get_monthly_totals()  # [{"month":"2026-02","total":220.0}, ...]
    m_map = {r["month"]: r["total"] for r in monthly}
    this_total = float(m_map.get(month, 0.0))

    # Find previous month total (simple)
    prev_total = None
    try:
        dt = datetime.strptime(month + "-01", "%Y-%m-%d")
        prev_month = (dt.replace(day=1)).strftime("%Y-%m")
        # quick back 1 month (manual)
        y, mo = dt.year, dt.month
        if mo == 1:
            y, mo = y - 1, 12
        else:
            mo -= 1
        prev_month = f"{y:04d}-{mo:02d}"
        prev_total = float(m_map.get(prev_month, 0.0))
    except Exception:
        prev_total = None

    # 2) Category totals for the month
    cat_rows = [r for r in get_monthly_category_totals() if r["month"] == month]
    cat_rows_sorted = sorted(cat_rows, key=lambda x: x["total"], reverse=True)

    # 3) Budget alerts
    alerts = check_budget_overruns(month)

    # 4) Insights rules
    insights = []
    suggestions = []

    insights.append(f"Total spend for {month} is ₹{this_total:.0f}.")

    if prev_total is not None and prev_total > 0:
        diff = this_total - prev_total
        pct = (diff / prev_total) * 100
        if pct >= 20:
            insights.append(f"Spending increased by {pct:.0f}% vs last month.")
            suggestions.append("Try setting tighter category budgets for the top categories.")
        elif pct <= -20:
            insights.append(f"Spending reduced by {abs(pct):.0f}% vs last month. Good control!")
        else:
            insights.append("Spending is stable compared to last month.")

    if cat_rows_sorted:
        top1 = cat_rows_sorted[0]
        insights.append(f"Top category: {top1['category']} (₹{top1['total']:.0f}).")
        if len(cat_rows_sorted) > 1:
            top2 = cat_rows_sorted[1]
            insights.append(f"Second: {top2['category']} (₹{top2['total']:.0f}).")

        # Suggestion based on top category
        if top1["category"] in ["food", "entertainment"]:
            suggestions.append("Consider a weekly cap for eating-out/entertainment to avoid spikes.")
        if top1["category"] in ["groceries"]:
            suggestions.append("Track grocery list + avoid duplicate buys (helps reduce waste).")

    # Budget alert suggestions
    if alerts:
        for a in alerts:
            suggestions.append(
                f"Budget exceeded in {a['category']}: overshoot ₹{a['overshoot']:.0f}. Reduce by ~₹{a['overshoot']/4:.0f} per week."
            )
    else:
        suggestions.append("No budget overshoots detected for this month ✅")

    return {
        "month": month,
        "total": this_total,
        "insights": insights,
        "budget_alerts": alerts,
        "suggestions": suggestions,
    }

from sqlalchemy import func
from app.db.models import Expense

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

def get_range_total(start_date: str, end_date: str) -> float:
    db = SessionLocal()
    total = (
        db.query(func.sum(Expense.amount))
        .filter(Expense.date >= start_date, Expense.date <= end_date)
        .scalar()
    )
    db.close()
    return float(total or 0)