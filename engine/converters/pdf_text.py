"""PDF text extraction, search, and page info."""
import os, re
from engine.utils import safe_run

def extract_text(pdf_path, output_path=None):
    """Extract text from PDF using pdftotext."""
    if not os.path.exists(pdf_path):
        return {"success": False, "error": "File not found"}
    result = safe_run(["pdftotext", pdf_path, "-"], timeout=30)
    if result["success"]:
        text = result["stdout"].strip()
        if output_path:
            with open(output_path, 'w') as f: f.write(text)
        return {"success": True, "text": text, "pages": text.count('\f') + 1}
    return {"success": False, "error": result["stderr"]}

def search_text(pdf_path, query, case_sensitive=False):
    """Search text in PDF, returns page numbers with matches."""
    result = extract_text(pdf_path)
    if not result["success"]:
        return result
    text = result["text"]
    pages = text.split('\f')
    flags = 0 if case_sensitive else re.IGNORECASE
    matches = []
    for i, page_text in enumerate(pages):
        for m in re.finditer(re.escape(query), page_text, flags):
            matches.append({"page": i + 1, "position": m.start()})
    return {"success": True, "query": query, "matches": matches, "total_matches": len(matches)}

def get_page_info(pdf_path):
    """Get PDF page information using pdfinfo and PyPDF2."""
    import PyPDF2
    if not os.path.exists(pdf_path):
        return {"success": False, "error": "File not found"}
    info = safe_run(["pdfinfo", pdf_path], timeout=10)
    page_info = {}
    if info["success"]:
        for line in info["stdout"].strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                page_info[key.strip().lower()] = val.strip()
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        page_info["total_pages"] = len(reader.pages)
        if reader.pages:
            page_info["page_size"] = str(reader.pages[0].mediabox)
    except Exception:
        pass
    page_info["success"] = True
    return page_info

def extract_images(pdf_path, output_path=None):
    """Extract pages as images using pdftoppm."""
    if not os.path.exists(pdf_path):
        return {"success": False, "error": "File not found"}
    if output_path is None:
        output_path = pdf_path.replace(".pdf", "_pages")
    result = safe_run(["pdftoppm", "-png", pdf_path, output_path], timeout=30)
    if result["success"]:
        base = output_path
        images = []
        i = 1
        while os.path.exists(f"{base}-{i:03d}.png"):
            images.append(f"{base}-{i:03d}.png")
            i += 1
        return {"success": True, "images": images, "count": len(images)}
    return {"success": False, "error": result["error"]}

def add_text_watermark(pdf_path, watermark_text="CONFIDENTIAL", output_path=None):
    """Add text watermark to PDF metadata using PyPDF2."""
    import PyPDF2
    if not os.path.exists(pdf_path):
        return {"success": False, "error": "File not found"}
    if output_path is None:
        base, ext = os.path.splitext(pdf_path)
        output_path = f"{base}_watermarked{ext}"
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({
            "/Title": watermark_text.upper(),
            "/Author": "ICON DocForge",
            "/Subject": f"Watermarked: {watermark_text}",
            "/Creator": "ICON DocForge",
            "/Producer": "PyPDF2"
        })
        with open(output_path, 'wb') as f:
            writer.write(f)
        return {"success": True, "output": output_path, "watermark": watermark_text}
    except Exception as e:
        return {"success": False, "error": str(e)}
