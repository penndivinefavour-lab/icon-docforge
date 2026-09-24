"""Images to PDF converter using fpdf2."""
import os
from fpdf import FPDF
from PIL import Image
from engine.utils import create_temp_dir, cleanup_temp, sanitize_filename
from engine.config import OUTPUT_DIR


def images_to_pdf(image_paths: list, output_path: str = None, page_size: str = "A4", 
                  orientation: str = "portrait", quality: int = 85, margins: dict = None) -> dict:
    """Convert multiple images to a single PDF."""
    if not image_paths:
        return {"success": False, "error": "No images provided"}
    for p in image_paths:
        if not os.path.exists(p):
            return {"success": False, "error": f"Image not found: {p}"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "images.pdf")
    try:
        if orientation == "landscape":
            pdf = FPDF(orientation="L", format=page_size)
        else:
            pdf = FPDF(orientation="P", format=page_size)
        margins = margins or {"top": 10, "bottom": 10, "left": 10, "right": 10}
        for img_path in image_paths:
            img = Image.open(img_path)
            img_w, img_h = img.size
            pdf.add_page()
            page_w = pdf.w
            page_h = pdf.h
            margin_w = page_w - margins["left"] - margins["right"]
            margin_h = page_h - margins["top"] - margins["bottom"]
            scale_w = margin_w / img_w
            scale_h = margin_h / img_h
            scale = min(scale_w, scale_h, 1.0)
            final_w = img_w * scale
            final_h = img_h * scale
            x = margins["left"] + (margin_w - final_w) / 2
            y = margins["top"] + (margin_h - final_h) / 2
            pdf.image(img_path, x=x, y=y, w=final_w, h=final_h)
        pdf.output(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "pages": len(image_paths), "method": "fpdf2"}
        return {"success": False, "error": "PDF not created"}
    except Exception as e:
        return {"success": False, "error": str(e)}
