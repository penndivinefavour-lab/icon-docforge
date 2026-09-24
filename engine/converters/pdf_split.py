"""PDF split using poppler pdfseparate."""
import os
import shutil
from engine.utils import safe_run
from engine.config import OUTPUT_DIR


def pdf_split(input_path: str, pages: str, output_path: str = None) -> dict:
    """Extract pages from a PDF using pdfseparate."""
    if not os.path.exists(input_path):
        return {"success": False, "error": f"PDF not found: {input_path}"}
    
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "split_output.pdf")
    
    page_nums = []
    for part in pages.replace(" ", "").split(","):
        if "-" in part:
            start, end = part.split("-")
            page_nums.extend(range(int(start), int(end) + 1))
        else:
            page_nums.append(int(part))
    
    if not page_nums:
        return {"success": False, "error": "No valid page numbers"}
    
    temp_dir = os.path.join(str(OUTPUT_DIR), "split_tmp")
    os.makedirs(temp_dir, exist_ok=True)
    
    extracted = []
    for i, page_num in enumerate(page_nums):
        page_file = os.path.join(temp_dir, f"df_split_{i:03d}.pdf")
        result = safe_run(["pdfseparate", "-f", str(page_num), "-l", str(page_num), input_path, page_file], timeout=30)
        if result["success"] and os.path.exists(page_file) and os.path.getsize(page_file) > 0:
            extracted.append(page_file)
    
    if not extracted:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return {"success": False, "error": "No pages extracted"}
    
    from engine.converters.pdf_merge import pdf_merge
    result = pdf_merge(extracted, output_path)
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return result
