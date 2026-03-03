import re

def detect_payment_mode(raw_text: str | None) -> str | None:
    if not raw_text:
        return None

    t = raw_text.lower()

    if re.search(r"\bupi\b|\bgpay\b|\bgoogle pay\b|\bphonepe\b|\bpaytm\b|\bbhim\b", t):
        return "UPI"
    if re.search(r"\bcredit\b|\bdebit\b|\bcard\b|\bvisa\b|\bmastercard\b|\brupay\b", t):
        return "CARD"
    if re.search(r"\bcash\b", t):
        return "CASH"

    return None