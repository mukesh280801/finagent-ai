from pydantic import BaseModel
from typing import Optional

class ReceiptOut(BaseModel):
    date: Optional[str] = None
    merchant: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "INR"
    category_hint: Optional[str] = None
    raw_text: Optional[str] = None
