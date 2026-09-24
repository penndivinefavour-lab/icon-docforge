"""PDF compression using pdftoppm at reduced DPI."""
import os
from engine.utils import safe_run

def compress_pdf(pdf_path, output_path=None, dpi=72):
    """Compress PDF by re-rendering at specified DPI using pdftoppm."""
    if not os.path.exists(pdf_path):
        return {"success": False, "error": "File not found"}
    if output_path is None:
        base, ext = os.path.splitext(pdf_path)
        output_path = f"{base}_compressed{ext}"
    result = safe_run(
        ["pdftoppm", "-r", str(dpi), "-png", pdf_path, output_path.replace(".pdf", "")],
        timeout=60
    )
    if result["success"]:
        base = output_path.replace(".pdf", "")
        images = []
        i = 1
        while os.path.exists(f"{base}-{i:03d}.png"):
            images.append(f"{base}-{i:03d}.png")
            i += 1
        return {"success": True, "output": output_path, "method": f"pdftoppm {dpi} DPI", "pages": len(images)}
    return {"success": False, "error": result["error"]}
