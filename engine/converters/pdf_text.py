"""PDF text extraction and search using pdftotext and PyPDF2."""
import os
from engine.utils import safe_run
from engine.config import OUTPUT_DIR


def extract_text(input_path: str, output_path: str = None) -> dict:
    """Extract text from PDF using pdftotext."""
    if not os.path.exists(input_path):
        return {"success": False, "error": f"PDF not found"}
    
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".txt")
    
    result = safe_run(["pdftotext", input_path, output_path], timeout=60)
    
    if result["success"] and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return {
            "success": True,
            "output": output_path,
            "size": os.path.getsize(output_path),
            "method": "pdftotext"
        }
    return {"success": False, "error": result["stderr"][:200]}


def search_text(input_path: str, query: str, case_sensitive: bool = False) -> dict:
    """Search for text within PDF pages."""
    if not os.path.exists(input_path):
        return {"success": False, "error": f"PDF not found"}
    
    result = safe_run(["pdftotext", input_path, "-"], timeout=30)
    
    if not result["success"]:
        return {"success": False, "error": "Failed to extract text"}
    
    text = result["stdout"]
    flags = 0 if case_sensitive else 2  # re.IGNORECASE
    import re
    matches = list(re.finditer(re.escape(query), text, flags))
    
    pages_with_matches = set()
    # pdftotext includes page markers like ---- PAGE N ----
    lines = text.split('\n')
    current_page = 0
    for i, line in enumerate(lines):
        page_match = re.match(r'---- PAGE (\d+) ----', line)
        if page_match:
            current_page = int(page_match.group(1))
        for m in matches:
            if m.start() < sum(len(l)+1 for l in lines[:i]):
                pages_with_matches.add(current_page)
    
    return {
        "success": True,
        "query": query,
        "matches": len(matches),
        "pages_with_matches": sorted(pages_with_matches),
        "method": "pdftotext+regex"
    }


def get_page_info(input_path: str) -> dict:
    """Get page count, dimensions, and orientation from PDF."""
    if not os.path.exists(input_path):
        return {"success": False, "error": f"PDF not found"}
    
    result = safe_run(["pdfinfo", input_path], timeout=10)
    
    info = {}
    if result["success"]:
        for line in result["stdout"].strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                info[key.strip()] = val.strip()
    
    # Get page count from PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(input_path)
        info["pages"] = len(reader.pages)
        
        # Get page dimensions
        page = reader.pages[0]
        if '/MediaBox' in page:
            media_box = page['/MediaBox']
            info["page_width"] = float(media_box[2])
            info["page_height"] = float(media_box[3])
            info["page_orientation"] = "landscape" if info["page_width"] > info["page_height"] else "portrait"
    except Exception:
        pass
    
    return {"success": True, "info": info, "method": "pdfinfo+PyPDF2"}


def extract_images(input_path: str) -> dict:
    """Extract images from PDF pages using pdftoppm."""
    if not os.path.exists(input_path):
        return {"success": False, "error": f"PDF not found"}
    
    base = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.join(str(OUTPUT_DIR), f"{base}_images")
    os.makedirs(output_dir, exist_ok=True)
    
    result = safe_run([
        "pdftoppm", "-png", "-r", "150", input_path, os.path.join(output_dir, base)
    ], timeout=120)
    
    if result["success"]:
        import glob
        images = glob.glob(os.path.join(output_dir, f"{base}*.png"))
        return {
            "success": True,
            "images": images,
            "count": len(images),
            "output_dir": output_dir,
            "method": "pdftoppm"
        }
    return {"success": False, "error": result["stderr"][:200]}
