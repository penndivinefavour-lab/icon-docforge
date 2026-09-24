"""PDF page reordering using pdfseparate + pdfunite."""
import os
import shutil
from engine.utils import safe_run
from engine.config import OUTPUT_DIR


def reorder_pages(input_path: str, page_order: list, output_path: str = None) -> dict:
    """Reorder PDF pages by extracting and recombining in specified order.
    
    page_order: list of 1-based page numbers in desired order
    e.g., [3, 1, 2, 5, 4] puts page 3 first, then 1, 2, 5, 4
    """
    if not os.path.exists(input_path):
        return {"success": False, "error": f"PDF not found"}
    
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "reordered.pdf")
    
    # Get total pages
    info_result = safe_run(["pdfinfo", input_path], timeout=10)
    total_pages = 0
    if info_result["success"]:
        for line in info_result["stdout"].split('\n'):
            if line.startswith('Pages:'):
                total_pages = int(line.split(':')[1].strip())
    
    if not total_pages:
        # Try PyPDF2
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(input_path)
            total_pages = len(reader.pages)
        except:
            pass
    
    if not total_pages:
        return {"success": False, "error": "Could not determine page count"}
    
    # Validate page_order
    for p in page_order:
        if p < 1 or p > total_pages:
            return {"success": False, "error": f"Invalid page number: {p} (1-{total_pages})"}
    
    # Extract pages
    temp_dir = os.path.join(str(OUTPUT_DIR), "reorder_tmp")
    os.makedirs(temp_dir, exist_ok=True)
    
    extracted = []
    for i, page_num in enumerate(page_order):
        page_file = os.path.join(temp_dir, f"pg_{i:03d}.pdf")
        result = safe_run(["pdfseparate", "-f", str(page_num), "-l", str(page_num), 
                          input_path, page_file], timeout=30)
        if result["success"] and os.path.exists(page_file) and os.path.getsize(page_file) > 0:
            extracted.append(page_file)
    
    if not extracted:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return {"success": False, "error": "No pages extracted"}
    
    # Merge in new order
    from engine.converters.pdf_merge import pdf_merge
    result = pdf_merge(extracted, output_path)
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    return result


def delete_pages(input_path: str, pages_to_delete: list, output_path: str = None) -> dict:
    """Delete specified pages from PDF."""
    if not os.path.exists(input_path):
        return {"success": False, "error": f"PDF not found"}
    
    # Get total pages
    info_result = safe_run(["pdfinfo", input_path], timeout=10)
    total_pages = 0
    if info_result["success"]:
        for line in info_result["stdout"].split('\n'):
            if line.startswith('Pages:'):
                total_pages = int(line.split(':')[1].strip())
    
    if not total_pages:
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(input_path)
            total_pages = len(reader.pages)
        except:
            pass
    
    pages_to_keep = [p for p in range(1, total_pages + 1) if p not in pages_to_delete]
    
    if not pages_to_keep:
        return {"success": False, "error": "All pages would be deleted"}
    
    return reorder_pages(input_path, pages_to_keep, output_path)
