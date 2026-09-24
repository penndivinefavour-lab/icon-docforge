"""PDF merge using poppler pdfunite."""
import os
from engine.utils import safe_run
from engine.config import OUTPUT_DIR


def pdf_merge(pdf_paths: list, output_path: str = None) -> dict:
    """Merge multiple PDFs into one using pdfunite."""
    if len(pdf_paths) < 2:
        return {"success": False, "error": "Need at least 2 PDFs to merge"}
    
    for p in pdf_paths:
        if not os.path.exists(p):
            return {"success": False, "error": f"PDF not found: {p}"}
    
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "merged.pdf")
    
    result = safe_run(["pdfunite"] + pdf_paths + [output_path], timeout=120)
    
    if result["success"] and os.path.exists(output_path):
        return {
            "success": True,
            "output": output_path,
            "size": os.path.getsize(output_path),
            "pages_merged": len(pdf_paths),
            "method": "pdfunite"
        }
    return {"success": False, "error": result["stderr"][:200]}
