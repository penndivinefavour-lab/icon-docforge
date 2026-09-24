"""DOCX ↔ ODT converter using pandoc."""
import os
from engine.utils import safe_run
from engine.config import OUTPUT_DIR


def docx_to_odt(input_path: str, output_path: str = None) -> dict:
    """Convert DOCX to ODT using pandoc."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "DOCX not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".odt")
    result = safe_run(["pandoc", input_path, "-t", "odt", "-o", output_path], timeout=30)
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc"}
    return {"success": False, "error": result["stderr"][:200]}


def odt_to_docx(input_path: str, output_path: str = None) -> dict:
    """Convert ODT to DOCX using pandoc."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "ODT not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".docx")
    result = safe_run(["pandoc", input_path, "-t", "docx", "-o", output_path], timeout=30)
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc"}
    return {"success": False, "error": result["stderr"][:200]}
