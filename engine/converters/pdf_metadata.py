"""PDF metadata operations using pdfinfo and PyPDF2."""
import os
import PyPDF2
from engine.utils import safe_run


def read_pdf_metadata(input_path: str) -> dict:
    """Read PDF metadata using pdfinfo and PyPDF2."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "PDF not found"}
    
    result = safe_run(["pdfinfo", input_path], timeout=10)
    
    metadata = {}
    if result["success"]:
        for line in result["stdout"].strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                metadata[key.strip()] = val.strip()
    
    # Also get PyPDF2 metadata
    try:
        reader = PyPDF2.PdfReader(input_path)
        info = reader.metadata
        if info:
            metadata.update({k: str(v) for k, v in info.items() if v})
    except Exception:
        pass
    
    return {"success": True, "metadata": metadata, "method": "pdfinfo+PyPDF2"}


def update_pdf_metadata(input_path: str, output_path: str, metadata: dict) -> dict:
    """Update PDF metadata."""
    try:
        reader = PyPDF2.PdfReader(input_path)
        writer = PyPDF2.PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        # Set metadata
        for key, value in metadata.items():
            writer.add_metadata({f"/{key}": value})
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return {"success": True, "output": output_path, "method": "PyPDF2"}
    except Exception as e:
        return {"success": False, "error": str(e)}
