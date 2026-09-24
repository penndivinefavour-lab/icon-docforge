"""Markdown to PDF using pandoc + weasyprint."""
import os
from engine.utils import safe_run, create_temp_dir, cleanup_temp
from engine.config import OUTPUT_DIR


def markdown_to_pdf(input_path: str, output_path: str = None) -> dict:
    """Convert Markdown to PDF via pandoc→HTML→weasyprint."""
    if not os.path.exists(input_path):
        return {"success": False, "error": f"File not found"}
    
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    
    temp_dir = create_temp_dir("md2pdf_")
    try:
        # pandoc MD → HTML
        html_path = os.path.join(temp_dir, "output.html")
        result = safe_run(["pandoc", input_path, "-t", "html", "-o", html_path], timeout=30)
        if not result["success"]:
            return {"success": False, "error": result["stderr"][:200]}
        
        # weasyprint HTML → PDF
        from weasyprint import HTML
        HTML(filename=html_path).write_pdf(output_path)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc+weasyprint"}
        return {"success": False, "error": "PDF not created"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cleanup_temp(temp_dir)
