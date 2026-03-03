import re
from app.schemas.receipt import ReceiptOut

TOTAL_LINE_REGEX = re.compile(
    r"(?:grand\s*)?tot(?:al|at)\s*[:\-]?\s*(?:₹|rs\.?|inr)?\s*([0-9][0-9,]*\.?[0-9]{0,2})",
    re.IGNORECASE
)

# Money with decimals (120.00, 220.50)
MONEY_DEC_REGEX = re.compile(r"\b([0-9][0-9,]*\.[0-9]{2})\b")

# Money without decimals (6000, 4000) -> often means 60.00, 40.00 (OCR)
MONEY_NODEC_REGEX = re.compile(r"\b([0-9]{3,6})\b")

DATE_REGEX_1 = re.compile(r"\b(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})\b")
DATE_REGEX_2 = re.compile(r"\b(\d{4})[\/\-.](\d{4})\b")  # 1202/2026

def _clean_num(s: str) -> float:
    return float(s.replace(",", ""))

def _normalize_year(y: str) -> str:
    return "20" + y if len(y) == 2 else y

def _parse_amount_token(tok: str) -> float | None:
    """Convert token like '220.00' or '6000' to float."""
    tok = tok.replace(",", "").strip()
    if not tok:
        return None
    if "." in tok:
        try:
            return float(tok)
        except ValueError:
            return None
    # no-decimal OCR numbers like 6000 -> 60.00 (divide by 100)
    if tok.isdigit() and len(tok) >= 3:
        return int(tok) / 100.0
    return None

def _sum_item_amounts(raw: str) -> float | None:
    total = 0.0
    found = False
    for line in raw.splitlines():
        l = line.strip().lower()
        if not l:
            continue
        # skip header-ish lines
        if any(k in l for k in ["total", "totat", "grand", "bill", "date", "payment"]):
            continue

        # prefer decimal amounts in line
        mdec = MONEY_DEC_REGEX.findall(line)
        if mdec:
            amt = _parse_amount_token(mdec[-1])
            if amt is not None:
                total += amt
                found = True
            continue

        # fallback: no-decimal token (6000 -> 60.00)
        mnd = MONEY_NODEC_REGEX.findall(line)
        if mnd:
            amt = _parse_amount_token(mnd[-1])
            if amt is not None:
                total += amt
                found = True

    return round(total, 2) if found else None

def parse_receipt_text(text: str) -> ReceiptOut:
    raw = (text or "").strip()

    # merchant
    merchant = None
    for line in raw.splitlines():
        line = line.strip()
        if len(line) >= 3:
            merchant = line[:80]
            break

    # date
    date = None
    date_line = None
    for line in raw.splitlines():
        if "date" in line.lower():
            date_line = line
            break
    target = date_line or raw

    m1 = DATE_REGEX_1.search(target)
    if m1:
        dd, mm, yy = m1.group(1), m1.group(2), _normalize_year(m1.group(3))
        date = f"{yy.zfill(4)}-{mm.zfill(2)}-{dd.zfill(2)}"
    else:
        m2 = DATE_REGEX_2.search(target)
        if m2:
            ddmm = m2.group(1)
            yyyy = m2.group(2)
            dd, mm = ddmm[:2], ddmm[2:]
            date = f"{yyyy}-{mm}-{dd}"

    # amount: total-first, but validate using item sum
    amount = None
    total_amt = None

    mt = TOTAL_LINE_REGEX.search(raw)
    if mt:
        total_amt = _parse_amount_token(mt.group(1))

    items_sum = _sum_item_amounts(raw)

    # Decision logic:
    # If total exists and item sum exists:
    #   if total is wildly larger than sum -> use sum
    # else use whatever exists
    if total_amt is not None and items_sum is not None:
        # if total > 3x sum, OCR likely wrong (like 3220 vs 220)
        if total_amt > (items_sum * 3):
            amount = items_sum
        else:
            amount = total_amt
    elif total_amt is not None:
        amount = total_amt
    elif items_sum is not None:
        amount = items_sum
    else:
        amount = None

    return ReceiptOut(
        date=date,
        merchant=merchant,
        amount=amount,
        raw_text=raw
    )