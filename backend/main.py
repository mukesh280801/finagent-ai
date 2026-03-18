from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import pytesseract
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "FinAgent Backend Running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 🔥 OCR PART
    image = Image.open(file_path)
    extracted_text = pytesseract.image_to_string(image)

    # 🔥 Simple amount extraction
    import re
    amounts = re.findall(r'\d+\.\d+|\d+', extracted_text)

    total_amount = amounts[-1] if amounts else "Not found"

    return {
        "status": "success",
        "filename": file.filename,
        "extracted_text": extracted_text,
        "total_amount": total_amount
    }