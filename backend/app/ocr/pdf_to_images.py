import fitz  # PyMuPDF
from pathlib import Path

def pdf_to_images(pdf_path: str, out_dir: str) -> list[str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    image_paths = []

    for i in range(len(doc)):
        page = doc[i]
        pix = page.get_pixmap(dpi=200)
        img_path = out / f"page_{i+1}.png"
        pix.save(str(img_path))
        image_paths.append(str(img_path))

    doc.close()
    return image_paths
