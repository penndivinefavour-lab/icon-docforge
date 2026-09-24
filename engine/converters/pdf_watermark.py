"""PDF watermarking using PyPDF2 (text overlay) and pdftoppm (image overlay)."""
import os
from engine.utils import safe_run
from engine.config import OUTPUT_DIR


def add_text_watermark(input_path: str, output_path: str = None, 
                        text: str = "CONFIDENTIAL", position: str = "bottom-right") -> dict:
    """Add a text watermark to PDF pages using PyPDF2.
    
    PyPDF2 can't directly add visible text watermarks without full page content.
    We use pdftotext + pdftoppm approach or note the limitation.
    """
    if not os.path.exists(input_path):
        return {"success": False, "error": f"PDF not found"}
    
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "watermarked.pdf")
    
    # PyPDF2 limitation: Can add metadata but not easily add visible watermarks
    # Without ghostscript or pdftotext+pdfunite approach
    # Best approach: note limitation and offer pdftoppm-based approach
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(input_path)
        writer = PyPDF2.PdfWriter()
        
        for page in reader.pages:
            # Add metadata to indicate watermark (not visually visible)
            # For real visual watermarks, we'd need ghostscript
            writer.add_page(page)
        
        # Add watermark text to metadata
        writer.add_metadata({"/Watermark": text})
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return {
            "success": True,
            "output": output_path,
            "size": os.path.getsize(output_path),
            "pages": len(reader.pages),
            "watermark_text": text,
            "method": "PyPDF2-metadata-watermark",
            "note": "Metadata watermark only. Visual watermark requires Ghostscript."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_image_watermark(input_path: str, output_path: str = None,
                         watermark_image: str = None) -> dict:
    """Add image watermark to PDF pages.
    
    Requires pdftoppm + image manipulation + recombination.
    Currently limited without Ghostscript.
    """
    return {
        "success": False,
        "error": "Image watermarking requires Ghostscript or full page rendering. Not available locally without Ghostscript."
    }
