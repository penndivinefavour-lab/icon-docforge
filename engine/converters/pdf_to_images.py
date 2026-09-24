"""PDF to images using poppler pdftoppm."""
import os
from engine.utils import safe_run
from engine.config import OUTPUT_DIR


def pdf_to_images(input_path: str, output_path: str = None, format: str = "png", 
                  dpi: int = 150) -> dict:
    """Convert PDF pages to images using pdftoppm."""
    if not os.path.exists(input_path):
        return {"success": False, "error": f"PDF not found"}
    
    if output_path is None:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base}_pages")
    
    output_prefix = os.path.join(os.path.dirname(output_path), os.path.basename(output_path))
    
    result = safe_run([
        "pdftoppm", f"-{format}", f"-r", str(dpi), input_path, output_prefix
    ], timeout=120)
    
    if result["success"]:
        # Find generated files
        files = [f for f in os.listdir(os.path.dirname(output_prefix) or '.') 
                 if f.startswith(os.path.basename(output_prefix))]
        return {
            "success": True,
            "output": output_prefix,
            "files": files,
            "count": len(files),
            "method": "pdftoppm"
        }
    return {"success": False, "error": result["stderr"][:200]}
