"""PDF to Image Converter — ICON DocForge v1.3

Converts PDF pages to images using pypdfium2 (already installed in v1.2).
Enables OCR preprocessing by rasterizing PDF content.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Literal

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None  # type: ignore

from engine.utils import create_temp_dir


def pdf_to_images(
    input_path: str,
    output_prefix: Optional[str] = None,
    page_range: Optional[Tuple[int, int]] = None,
    dpi: int = 150,
    format: Literal["png", "jpeg", "webp"] = "png",
    quality: int = 95,
) -> dict:
    """Render PDF pages to images.
    
    Args:
        input_path: Path to source PDF
        output_prefix: Output filename prefix (without extension)
        page_range: (start, end) page range (1-indexed), None for all
        dpi: Render DPI
        format: Output image format (png, jpeg, webp)
        quality: JPEG/WebP quality (1-100)
    
    Returns:
        dict with keys: success, output, pages, errors
    """
    if pdfium is None:
        return {
            "success": False,
            "output": None,
            "pages": 0,
            "errors": ["pypdfium2 not installed. Run: pip install pypdfium2"],
        }
    
    try:
        # Validate input
        if not os.path.exists(input_path):
            return {"success": False, "output": None, "pages": 0, 
                   "errors": [f"Input file not found: {input_path}"]}
        
        # Open PDF
        pdf_document = pdfium.PdfDocument(input_path)
        total_pages = len(pdf_document)
        
        # Determine page range
        if page_range:
            start = max(1, min(page_range[0], total_pages))
            end = min(total_pages, max(page_range[0], page_range[1]))
        else:
            start, end = 1, total_pages
        
        # Set render scale based on DPI (standard PDF is 72 DPI)
        scale = int(dpi / 72.0)  # Convert to int for pypdfium2
        
        # Create output directory if needed
        if output_prefix:
            os.makedirs(os.path.dirname(output_prefix) or ".", exist_ok=True)
        
        rendered_files = []
        
        # Render each page
        for page_num in range(start, end + 1):
            page_index = page_num - 1  # Convert to 0-indexed
            
            page = pdf_document[page_index]
            
            # Render page to bitmap
            bitmap = page.render(
                scale=scale,
                no_rotate=False,
            )
            
            # Convert to PIL Image for format conversion
            from PIL import Image
            pil_image = bitmap.to_pil()
            
            # Save to file
            if output_prefix:
                ext = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}[format]
                output_path = f"{output_prefix}_{page_num:03d}{ext}"
            else:
                # Create temporary output
                temp_dir = create_temp_dir("ocr_render")
                ext = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}[format]
                output_path = os.path.join(temp_dir, f"_page_{page_num:03d}{ext}")
            
            # Save with appropriate settings
            save_kwargs = {}
            if format in ("jpeg", "webp"):
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True
            
            pil_image.save(output_path, **save_kwargs)
            rendered_files.append(output_path)
            
            # Clean up bitmap
            del bitmap
        
        # Close PDF document
        pdf_document.close()
        
        return {
            "success": True,
            "output": rendered_files,
            "pages": len(rendered_files),
            "total_pdf_pages": total_pages,
            "rendered_pages": list(range(start, end + 1)),
            "dpi": dpi,
            "format": format,
            "file_size": sum(os.path.getsize(f) for f in rendered_files) if rendered_files else 0,
            "errors": [],
        }
    
    except Exception as e:
        return {
            "success": False,
            "output": None,
            "pages": 0,
            "errors": [str(e)],
        }


def extract_page_image(
    input_path: str,
    page_num: int,
    dpi: int = 150,
) -> dict:
    """Extract a single page from PDF as an image.
    
    Args:
        input_path: Path to PDF
        page_num: Page number (1-indexed)
        dpi: Render DPI
    
    Returns:
        dict with keys: success, image_path, dimensions
    """
    if pdfium is None:
        return {"success": False, "image_path": None, "dimensions": None,
                "errors": ["pypdfium2 not installed"]}
    
    try:
        pdf_document = pdfium.PdfDocument(input_path)
        
        if page_num < 1 or page_num > len(pdf_document):
            return {"success": False, "image_path": None, "dimensions": None,
                    "errors": [f"Invalid page number: {page_num} (PDF has {len(pdf_document)} pages)"]}
        
        scale = dpi / 72.0
        page = pdf_document[page_num - 1]
        bitmap = page.render(scale=scale)
        pil_image = bitmap.to_pil()
        
        # Create temp output
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_path = tmp.name
            pil_image.save(output_path)
        
        width, height = pil_image.size
        pdf_document.close()
        
        return {
            "success": True,
            "image_path": output_path,
            "dimensions": (width, height),
            "dpi": dpi,
            "errors": [],
        }
    
    except Exception as e:
        return {"success": False, "image_path": None, "dimensions": None, "errors": [str(e)]}


if __name__ == "__main__":
    # Self-test
    import sys
    print("PDF to Image Converter — Self Test")
    print("=" * 50)
    
    # Check dependency
    if pdfium is None:
        print("❌ pypdfium2 not installed")
        sys.exit(1)
    
    print(f"✅ pypdfium2 v{pdfium.__version__} available")
    print("\nReady for PDF-to-image conversion.")
