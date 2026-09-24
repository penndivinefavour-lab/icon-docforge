"""PDF page reorder and delete using pdfseparate + pdfunite."""
import os
from engine.utils import safe_run

def reorder_pages(pdf_path, page_order, output_path=None):
    """Reorder PDF pages by extracting and recombining."""
    if not os.path.exists(pdf_path):
        return {"success": False, "error": "File not found"}
    total_pages = _get_page_count(pdf_path)
    if not total_pages:
        return {"success": False, "error": "Cannot determine page count"}
    for p in page_order:
        if p < 1 or p > total_pages:
            return {"success": False, "error": f"Page {p} out of range [1-{total_pages}]"}
    if output_path is None:
        base, ext = os.path.splitext(pdf_path)
        output_path = f"{base}_reordered{ext}"
    temp_dir = os.path.dirname(output_path) or "."
    temp_files = []
    for i, page_num in enumerate(page_order):
        temp_file = os.path.join(temp_dir, f"page_{i:03d}.pdf")
        result = safe_run(["pdfseparate", "-f", str(page_num), "-l", str(page_num), pdf_path, temp_file], timeout=15)
        if result["success"] and os.path.exists(temp_file):
            temp_files.append(temp_file)
        else:
            return {"success": False, "error": f"Failed to extract page {page_num}"}
    result = safe_run(["pdfunite"] + temp_files + [output_path], timeout=30)
    for tf in temp_files:
        if os.path.exists(tf): os.remove(tf)
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "order": page_order}
    return {"success": False, "error": result["error"]}

def delete_pages(pdf_path, pages_to_delete, output_path=None):
    """Delete specified pages from PDF."""
    if not os.path.exists(pdf_path):
        return {"success": False, "error": "File not found"}
    total_pages = _get_page_count(pdf_path)
    if not total_pages:
        return {"success": False, "error": "Cannot determine page count"}
    delete_set = set(pages_to_delete)
    keep_order = [i for i in range(1, total_pages + 1) if i not in delete_set]
    if not keep_order:
        return {"success": False, "error": "All pages would be deleted"}
    return reorder_pages(pdf_path, keep_order, output_path)

def _get_page_count(pdf_path):
    from engine.utils import safe_run
    result = safe_run(["pdfinfo", pdf_path], timeout=10)
    if result["success"]:
        for line in result["stdout"].strip().split('\n'):
            if line.lower().startswith("pages:"):
                try:
                    return int(line.split(":")[1].strip())
                except ValueError:
                    return 0
    import PyPDF2
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        return len(reader.pages)
    except Exception:
        return 0
