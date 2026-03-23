from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import pytesseract
from PIL import Image
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 🔥 OCR
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)

    amounts = re.findall(r'\d+\.\d+|\d+', text)
    total = amounts[-1] if amounts else "Not found"

    return {
        "text": text,
        "total_amount": total
    }