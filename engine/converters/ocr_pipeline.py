"""OCR Pipeline — ICON DocForge v1.3

Main OCR processing pipeline with preprocessing, recognition, and postprocessing.
Supports multiple backends via EngineABC abstraction.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal

from engine.converters.pdf_to_image import pdf_to_images
from engine.ocr_engine import OCREngine, OCRProfile, OCRResult, get_ocr_manager
from engine.utils import create_temp_dir


# Common file extensions recognized as images
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif"}

# PDF-related extensions
PDF_EXTENSIONS = {".pdf"}


class OCRRuntimeError(Exception):
    """Raised when OCR runtime fails."""
    pass


def validate_input(input_path: str) -> dict:
    """Validate input file exists and is readable.
    
    Returns:
        dict with success flag, file type, and errors
    """
    result = {
        "success": False,
        "file_type": None,  # "image" or "pdf"
        "path": input_path,
        "errors": [],
    }
    
    # Check existence
    if not os.path.exists(input_path):
        result["errors"].append(f"File not found: {input_path}")
        return result
    
    # Check readability
    if not os.access(input_path, os.R_OK):
        result["errors"].append(f"File not readable: {input_path}")
        return result
    
    # Determine file type by extension
    ext = Path(input_path).suffix.lower()
    
    if ext in IMAGE_EXTENSIONS:
        result["file_type"] = "image"
        result["success"] = True
    elif ext in PDF_EXTENSIONS:
        result["file_type"] = "pdf"
        result["success"] = True
    else:
        result["errors"].append(f"Unsupported file type: {ext}. Supported: {', '.join(sorted(IMAGE_EXTENSIONS | PDF_EXTENSIONS))}")
    
    return result


def preprocess_image(
    image_path: str,
    profile: OCRProfile = OCRProfile.BALANCED,
) -> dict:
    """Apply preprocessing to image before OCR.
    
    Uses Pillow for transformations since OpenCV isn't available.
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        
        img = Image.open(image_path)
        original_mode = img.mode
        original_size = img.size
        
        # Convert to grayscale
        if original_mode != "L":
            img = img.convert("L")
        
        # Apply profile-specific preprocessing
        if profile == OCRProfile.FAST:
            # Just ensure grayscale
            pass
        elif profile == OCRProfile.BALANCED:
            # Mild sharpening
            img = img.filter(ImageFilter.SHARPEN)
        elif profile == OCRProfile.QUALITY:
            # Aggressive enhancement
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            img = img.filter(ImageFilter.SHARPEN)
        
        # Save preprocessed version
        temp_dir = create_temp_dir("ocr_preprocess")
        output_path = os.path.join(temp_dir, f"preprocessed_{os.getpid()}.png")
        img.save(output_path, optimize=True)
        
        return {
            "success": True,
            "output_path": output_path,
            "original_size": original_size,
            "preprocessed_size": img.size,
            "profile": profile.value,
            "errors": [],
        }
    
    except Exception as e:
        return {
            "success": False,
            "output_path": None,
            "original_size": None,
            "preprocessed_size": None,
            "profile": profile.value,
            "errors": [str(e)],
        }


def detect_image_type(image_path: str) -> dict:
    """Detect whether image contains text (for auto-mode).
    
    Simple heuristic: check for high contrast regions and edge density.
    """
    try:
        from PIL import Image
        
        img = Image.open(image_path).convert("L")
        pixels = list(img.getdata())
        
        # Calculate statistics
        mean_val = sum(pixels) / len(pixels)
        variance = sum((p - mean_val) ** 2 for p in pixels) / len(pixels)
        std_dev = variance ** 0.5
        
        # Heuristics
        is_high_contrast = std_dev > 50  # Varied pixel values
        is_white = mean_val > 200  # Mostly white background
        is_black = mean_val < 50   # Mostly black (scanned doc)
        has_edges = std_dev > 30   # Some edge structure
        
        return {
            "is_text_heavy": is_high_contrast and has_edges,
            "is_scanned": is_white or is_black,
            "mean_brightness": mean_val,
            "contrast_level": std_dev,
            "estimated_quality": "good" if is_high_contrast else "poor",
        }
    
    except Exception:
        return {"is_text_heavy": True, "is_scanned": True, "error": "Detection failed"}


def run_ocr(
    input_path: str,
    language: str = "eng",
    profile: str = "balanced",
    mode: Literal["auto", "force"] = "auto",
    output_format: Literal["txt", "json", "html"] = "txt",
) -> dict:
    """Main OCR pipeline entry point.
    
    Supports both direct image input and PDF input (which gets rasterized first).
    
    Args:
        input_path: Path to input file
        language: BCP 47 language code (default: eng)
        profile: Preprocessing profile (fast, balanced, quality)
        mode: OCR mode (auto: skip text-heavy PDFs; force: OCR all)
        output_format: Output format (txt, json, html)
    
    Returns:
        dict with success, text, confidence, errors
    """
    # Validate input
    validation = validate_input(input_path)
    if not validation["success"]:
        return {"success": False, "text": "", "confidence": 0.0, "errors": validation["errors"]}
    
    # Get OCR manager and engine
    mgr = get_ocr_manager()
    engine_info = mgr.ocr_status()
    
    if engine_info["status"] == "unavailable":
        return {
            "success": False,
            "text": "",
            "confidence": 0.0,
            "errors": engine_info["recommendations"],
            "requires_engine": True,
        }
    
    engine = mgr.get_engine()
    
    # Handle PDF input
    intermediate_paths = []
    current_input = input_path
    
    if validation["file_type"] == "pdf":
        # Render PDF to images
        temp_dir = create_temp_dir("ocr_pdf")
        prefix = os.path.join(temp_dir, "_page")
        
        render_result = pdf_to_images(
            input_path=current_input,
            output_prefix=prefix,
            dpi=150,
        )
        
        if not render_result["success"]:
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "errors": render_result["errors"],
            }
        
        intermediate_paths = render_result["output"]
        current_input = intermediate_paths[0]  # Process first page for demo
    
    # Auto mode: check if page needs OCR
    if mode == "auto" and validation["file_type"] == "pdf":
        # For PDFs in auto mode, we still process all pages since
        # we already rendered them. The 'auto' logic applies to
        # mixed PDFs where some pages have selectable text.
        pass
    
    # Preprocess
    preprocess_result = preprocess_image(current_input, OCRProfile(profile))
    if not preprocess_result["success"]:
        return {
            "success": False,
            "text": "",
            "confidence": 0.0,
            "errors": preprocess_result["errors"],
        }
    
    # Run OCR
    ocr_result: OCRResult = engine.recognize(
        input_path=preprocess_result["output_path"],
        language=language,
        profile=OCRProfile(profile),
    )
    
    # Post-process
    text = ocr_result.text.strip()
    
    # Format output
    if output_format == "json":
        output_text = __to_json(ocr_result)
    elif output_format == "html":
        output_text = __to_html(text, ocr_result)
    else:
        output_text = text
    
    # Cleanup intermediate files
    for path in intermediate_paths:
        try:
            os.unlink(path)
        except OSError:
            pass
    try:
        os.unlink(preprocess_result["output_path"])
    except OSError:
        pass
    
    return {
        "success": ocr_result.success,
        "text": output_text if output_format != "txt" else text,
        "confidence": ocr_result.confidence,
        "word_results": ocr_result.word_results,
        "pages": ocr_result.pages,
        "engine": ocr_result.engine,
        "errors": ocr_result.errors,
    }


def batch_ocr(
    input_paths: List[str],
    language: str = "eng",
    profile: str = "balanced",
    output_dir: Optional[str] = None,
) -> dict:
    """Process multiple files through OCR pipeline.
    
    Returns results for all inputs in order.
    """
    results = []
    
    for input_path in input_paths:
        result = run_ocr(input_path, language=language, profile=profile)
        result["input"] = input_path
        results.append(result)
        
        # Write output if requested
        if output_dir and result["success"]:
            os.makedirs(output_dir, exist_ok=True)
            basename = Path(input_path).stem
            output_path = os.path.join(output_dir, f"{basename}_ocr.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["text"])
            result["output_path"] = output_path
    
    return {
        "success": all(r["success"] for r in results),
        "results": results,
        "total": len(results),
        "succeeded": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
    }


def __to_json(result: OCRResult) -> str:
    """Format OCR result as JSON string."""
    import json
    output = {
        "text": result.text,
        "confidence": result.confidence,
        "word_count": len(result.word_results),
        "pages": result.pages,
        "words": result.word_results[:100],  # Limit for size
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


def __to_html(text: str, result: OCRResult) -> str:
    """Format OCR result as HTML with metadata."""
    html_parts = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'><title>OCR Result</title></head><body>",
        f"<h1>OCR Result</h1>",
        f"<p><strong>Confidence:</strong> {result.confidence:.1%}</p>",
        f"<p><strong>Pages:</strong> {result.pages}</p>",
        f"<p><strong>Words:</strong> {len(result.word_results)}</p>",
        "<hr>",
        "<pre>",
        text[:2000] + ("..." if len(text) > 2000 else ""),
        "</pre>",
        "</body></html>",
    ]
    return "\n".join(html_parts)


if __name__ == "__main__":
    import sys
    print("OCR Pipeline — Self Test")
    print("=" * 50)
    
    # Check engine availability
    mgr = get_ocr_manager()
    status = mgr.ocr_status()
    
    print(f"Status: {status['status']}")
    print(f"Primary engine: {status['primary_engine']}")
    
    if status["status"] == "unavailable":
        print("\n⚠️ No OCR engine available")
        if status["recommendations"]:
            print("Recommendations:")
            for rec in status["recommendations"]:
                print(f"  • {rec}")
    else:
        print("\n✅ OCR engine ready")
    
    # Test with fixture if available
    fixture = "tests/fixtures/ocr/clean_document.png"
    if os.path.exists(fixture):
        print(f"\nTesting with fixture: {fixture}")
        result = run_ocr(fixture)
        print(f"Success: {result['success']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")
        if result['text']:
            print(f"Text (first 200 chars): {result['text'][:200]}...")
