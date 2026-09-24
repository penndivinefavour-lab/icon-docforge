"""DOCX to PDF converter using pandoc + weasyprint as fallback."""
import subprocess
import os
import tempfile
from engine.utils import safe_run, create_temp_dir, cleanup_temp
from engine.config import TEMP_DIR, OUTPUT_DIR


def docx_to_pdf(input_path: str, output_path: str = None) -> dict:
    """Convert DOCX to PDF.
    
    Strategy: pandoc DOCX → HTML → weasyprint → PDF
    This avoids needing pdflatex which is not available on Termux.
    """
    if not os.path.exists(input_path):
        return {"success": False, "error": f"Input file not found: {input_path}"}
    
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else OUTPUT_DIR, exist_ok=True)
    temp_dir = create_temp_dir("docx2pdf_")
    
    try:
        # Step 1: pandoc DOCX → HTML
        html_path = os.path.join(temp_dir, "output.html")
        result = safe_run([
            "pandoc", input_path, "-t", "html", "-o", html_path
        ], timeout=60)
        
        if not result["success"]:
            return {"success": False, "error": f"Pandoc HTML conversion failed: {result['stderr'][:200]}"}
        
        # Step 2: weasyprint HTML → PDF
        from weasyprint import HTML
        HTML(filename=html_path).write_pdf(output_path)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return {
                "success": True,
                "output": output_path,
                "size": os.path.getsize(output_path),
                "method": "pandoc+weasyprint"
            }
        return {"success": False, "error": "Output PDF not created"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cleanup_temp(temp_dir)


def docx_to_odt(input_path: str, output_path: str = None) -> dict:
    """Convert DOCX to ODT using pandoc."""
    if not os.path.exists(input_path):
        return {"success": False, "error": f"Input file not found"}
    
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".odt")
    
    result = safe_run(["pandoc", input_path, "-t", "odt", "-o", output_path], timeout=30)
    
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc"}
    return {"success": False, "error": result["stderr"][:200]}
