import os
import pytesseract
from PIL import Image
import cv2
from app.ocr.preprocess import preprocess_image

# -----------------------------
# 1️⃣ Force Tesseract path (Windows fix)
# -----------------------------
TESS_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESS_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESS_PATH
else:
    print("⚠️ Tesseract not found at expected location.")


# -----------------------------
# 2️⃣ OCR Function
# -----------------------------
def ocr_text(img_path: str) -> str:
    """
    Takes image path → returns extracted raw text
    """

    try:
        # Preprocess image (grayscale, threshold etc.)
        img = preprocess_image(img_path)

        # Run OCR
        text = pytesseract.image_to_string(img)

        return text.strip()

    except Exception as e:
        print("❌ OCR ERROR:", str(e))
        return f"OCR Failed: {str(e)}"