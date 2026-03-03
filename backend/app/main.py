from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import uuid

from app.db.base import init_db
from app.ocr.extract import ocr_text
from app.services.parser import parse_receipt_text
from app.agents.classify import classify
from app.db.crud import create_expense, get_category_totals
from app.ocr.pdf_to_images import pdf_to_images
from app.utils.payment import detect_payment_mode
from app.db.crud import get_monthly_totals, get_monthly_category_totals
from app.db.crud import set_budget, get_all_budgets, check_budget_overruns 
from app.services.advisor import generate_monthly_advice
from app.services.reports import weekly_report
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FINAGENT.AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Storage Setup
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]  # backend/
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# DB Init
# -----------------------------
@app.on_event("startup")
def startup_event():
    init_db()


# -----------------------------
# Root
# -----------------------------
@app.get("/")
def home():
    return {"status": "ok", "service": "FINAGENT.AI"}


# -----------------------------
# Upload
# -----------------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    name = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / name
    path.write_bytes(await file.read())

    pages = []
    if ext == ".pdf":
        out_dir = UPLOAD_DIR / f"{name}_pages"
        pages = pdf_to_images(str(path), str(out_dir))

    return {"status": "ok", "file_id": name, "pdf_pages": pages}


# -----------------------------
# OCR
# -----------------------------
@app.get("/ocr/{file_id}")
def run_ocr(file_id: str):
    path = UPLOAD_DIR / file_id

    if not path.exists():
        return {"error": "File not found"}

    text = ocr_text(str(path))
    return {"file_id": file_id, "raw_text": text[:2000]}


# -----------------------------
# Extract
# -----------------------------
@app.get("/extract/{file_id}")
def extract(file_id: str):
    path = UPLOAD_DIR / file_id

    if not path.exists():
        return {"error": "File not found"}

    text = ocr_text(str(path))
    data = parse_receipt_text(text)
    category = classify(data.merchant, text)

    out = data.model_dump()
    out["category_hint"] = category
    return out


# -----------------------------
# Save (WITH Payment Mode)
# -----------------------------
@app.post("/save/{file_id}")
def save(file_id: str):
    path = UPLOAD_DIR / file_id

    if not path.exists():
        return {"error": "File not found"}

    text = ocr_text(str(path))
    data = parse_receipt_text(text)

    category = classify(data.merchant, text)
    payment_mode = detect_payment_mode(data.raw_text)

    exp = create_expense(
        file_id=file_id,
        date=data.date,
        merchant=data.merchant,
        amount=data.amount,
        category=category,
        payment_mode=payment_mode
    )

    return {
        "status": "saved",
        "expense_id": exp.id,
        "category": exp.category,
        "payment_mode": payment_mode
    }


# -----------------------------
# Analytics
# -----------------------------
@app.get("/analytics/category_totals")
def analytics_category():
    return get_category_totals()

@app.get("/analytics/monthly_trend")
def monthly_trend():
    return get_monthly_totals()


@app.get("/analytics/monthly_category_trend")
def monthly_category_trend():
    return get_monthly_category_totals()  

@app.post("/budget/set")
def budget_set(category: str, monthly_limit: float):
    b = set_budget(category, monthly_limit)
    return {"status": "ok", "category": b.category, "monthly_limit": b.monthly_limit}


@app.get("/budget/list")
def budget_list():
    return get_all_budgets()


@app.get("/watchdog/{month}")
def watchdog(month: str):
    # month example: 2026-02
    alerts = check_budget_overruns(month)
    return {"month": month, "alerts": alerts, "status": "ok"}

@app.get("/advisor/{month}")
def advisor(month: str):
    # month should be 'YYYY-MM' like 2026-02
    return generate_monthly_advice(month)

@app.get("/reports/weekly")
def weekly(start: str, end: str):
    # start/end format: YYYY-MM-DD
    return weekly_report(start, end)