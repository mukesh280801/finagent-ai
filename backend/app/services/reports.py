from app.db.crud import (
    get_range_total,
    get_range_category_totals,
    get_range_payment_totals,
    get_range_top_merchants,
)

def weekly_report(start_date: str, end_date: str):
    total = get_range_total(start_date, end_date)
    cats = get_range_category_totals(start_date, end_date)
    pays = get_range_payment_totals(start_date, end_date)
    merchants = get_range_top_merchants(start_date, end_date, limit=5)

    insights = []
    suggestions = []

    insights.append(f"Total spend from {start_date} to {end_date} is ₹{total:.0f}.")

    if cats:
        top = cats[0]
        insights.append(f"Top category: {top['category']} (₹{top['total']:.0f}).")
        if top["category"] in ["food", "entertainment"]:
            suggestions.append("Try setting a weekly cap for eating-out/entertainment.")
        if top["category"] == "groceries":
            suggestions.append("Plan grocery list and avoid repeated purchases.")

    if pays:
        top_pay = pays[0]
        insights.append(f"Most used payment: {top_pay['payment_mode']} (₹{top_pay['total']:.0f}).")

    if merchants:
        insights.append(f"Top merchant: {merchants[0]['merchant']} (₹{merchants[0]['total']:.0f}).")

    if not suggestions:
        suggestions.append("Looks stable ✅ Keep tracking your spending weekly.")

    return {
        "range": {"start": start_date, "end": end_date},
        "total": total,
        "category_totals": cats,
        "payment_totals": pays,
        "top_merchants": merchants,
        "insights": insights,
        "suggestions": suggestions
    }