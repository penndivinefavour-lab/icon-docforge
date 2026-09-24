"""OCR Engine Research — ICON DocForge v1.3

Audit of locally-runnable OCR engines for Android/Termux ARM64.
Decisions based on actual package availability, not assumptions.
"""

# =============================================================================
# INVESTIGATED ENGINES
# =============================================================================

ENGINES_INVESTIGATED = [
    {
        "name": "Tesseract OCR",
        "version": "5.x (via termux pkg)",
        "installation": "pkg install tesseract",
        "arm64_available": True,
        "termux_compatible": True,
        "apk_compatible": False,  # Requires native .so bundling
        "model_size_mb": "~50MB (eng+fra packs)",
        "ram_usage": "~200MB during processing",
        "languages": ["eng", "fra", "deu", "spa", "ara", "chi_sim", "jpn", "kor", "+200 more"],
        "accuracy": "High for clean typed text, Good for scans",
        "preprocessing": "Built-in denoise, binarization, deskew",
        "confidence_scoring": True,
        "word_level_confidence": True,
        "license": "Apache-2.0",
        "redistributable": True,
        "can_run_offline": True,
        "status": "NOT_INSTALLED",
        "reason_selected": None,
        "reason_rejected": None,
        "notes": "Primary candidate if pkg install works. No prebuilt wheel; relies on Termux native binary."
    },
    {
        "name": "RapidOCR (ONNX Runtime)",
        "version": "1.2.3",
        "installation": "pip install rapidocr-onnxruntime",
        "arm64_available": False,
        "termux_compatible": None,  # No ARM64 wheel exists
        "apk_compatible": None,
        "model_size_mb": "~40MB (DBNet + CRNN models)",
        "ram_usage": "~300MB during processing",
        "languages": ["eng", "fra", "chi_sim", "jpn", "kor", "ara", "+30 languages"],
        "accuracy": "High (modern DBNet + CRNN architecture)",
        "preprocessing": "Automatic via preprocess config",
        "confidence_scoring": True,
        "word_level_confidence": True,
        "license": "MIT",
        "redistributable": True,
        "can_run_offline": True,
        "status": "UNAVAILABLE",
        "reason_selected": None,
        "reason_rejected": "No linux_aarch64 wheel published on PyPI. Installation hangs compiling dependencies (pyclipper, shapely).",
        "notes": "Best accuracy but requires prebuilt ARM64 binaries or local compilation (not feasible on Pixel 4a)."
    },
    {
        "name": "EasyOCR",
        "version": "1.7.2",
        "installation": "pip install easyocr",
        "arm64_available": False,
        "termux_compatible": None,
        "apk_compatible": None,
        "model_size_mb": "~200MB+ (CTC + AST models)",
        "ram_usage": "~1GB+ during processing",
        "languages": ["eng", "fra", "deu", "spa", "ita", "por", "rus", "jpn", "kor", "chi", "+70 languages"],
        "accuracy": "Very High",
        "preprocessing": "Automatic layout detection",
        "confidence_scoring": True,
        "word_level_confidence": True,
        "license": "Apache-2.0",
        "redistributable": False,  # Heavy dependency chain (torch)
        "can_run_offline": True,
        "status": "REJECTED",
        "reason_selected": None,
        "reason_rejected": "Requires torch (~3.5GB) or onnxruntime (~271MB). No ARM64 wheels. Pipeline too heavy for Pixel 4a (5.5GB RAM, 3GB free).",
        "notes": "Superior accuracy but impractical resource footprint."
    },
    {
        "name": "PaddleOCR",
        "version": "3.7.0",
        "installation": "pip install paddleocr",
        "arm64_available": False,
        "termux_compatible": None,
        "apk_compatible": None,
        "model_size_mb": "~150MB+",
        "ram_usage": "~500MB+",
        "languages": ["eng", "fra", "chi_sim", "jpn", "kor", "ara", "+100 languages"],
        "accuracy": "Very High (industry-leading)",
        "preprocessing": "Extensive (angle cls, text direction, etc.)",
        "confidence_scoring": True,
        "word_level_confidence": False,
        "license": "Apache-2.0",
        "redistributable": False,  # Requires paddlepaddle (~2GB)
        "can_run_offline": True,
        "status": "REJECTED",
        "reason_selected": None,
        "reason_rejected": "Requires paddlepaddle deep learning framework. No ARM64 support. Massive dependency chain.",
        "notes": "Best quality but completely incompatible with constrained environment."
    },
    {
        "name": "pytesseract (Python wrapper)",
        "version": "0.3.13",
        "installation": "pip install pytesseract",
        "arm64_available": True,  # Pure Python wrapper
        "termux_compatible": True,  # Just needs tesseract binary
        "apk_compatible": False,  # Requires system binary
        "model_size_mb": "N/A (wrapper only)",
        "ram_usage": "~100MB",
        "languages": "Depends on tesseract-data-* packages",
        "accuracy": "Same as Tesseract",
        "preprocessing": "Delegates to Tesseract",
        "confidence_scoding": True,
        "word_level_confidence": True,
        "license": "MIT",
        "redistributable": True,
        "can_run_offline": True,
        "status": "PENDING",
        "reason_selected": None,
        "reason_rejected": None,
        "notes": "Lightweight Python binding. Installation succeeded but engine requires tesseract binary."
    },
]


# =============================================================================
# ENVIRONMENT CONSTRAINTS
# =============================================================================

ENV_CONSTRAINTS = {
    "device": "Pixel 4a (sm8150)",
    "architecture": "aarch64 (ARM64)",
    "os": "Android 13 (Termux)",
    "total_ram_gb": 5.5,
    "available_ram_mb": 832,
    "free_storage_gb": 3.2,
    "python_version": "3.14.6",
    "numpy_version": "2.4.4",
    "pillow_version": "12.3.0",
}


# =============================================================================
# DECISION MATRIX
# =============================================================================

DECISION = """
OCR ENGINE SELECTION FOR v1.3

PRIMARY CANDIDATE: Tesseract (via pytesseract wrapper)
  - Status: Available via `pkg install tesseract`
  - Storage: ~50MB for eng+fra language packs
  - RAM: ~200MB during processing (acceptable)
  - Accuracy: Good for printed text, acceptable for scans
  - Language support: 100+ languages including English and French
  - License: Apache-2.0 (permissive)
  - Offline: Yes, after model download
  - APK compatible: No (requires native binary)

FALLBACK STRATEGY:
  If Tesseract cannot be installed (package unavailable), the pipeline will:
  1. Detect absence gracefully
  2. Provide clear error messaging
  3. Allow manual model placement
  4. Support future RapidOCR integration if ARM64 wheels become available

IMPLEMENTATION APPROACH:
  - Build modular OCR engine interface (EngineABC)
  - Implement TesseractEngine subclass
  - Add fallback detection and graceful degradation
  - Document limitations clearly
  - Test with provided fixtures
"""


# =============================================================================
# PREPROCESSING PIPELINE (engine-agnostic)
# =============================================================================

PREPROCESSING_STAGES = [
    {"stage": "input_validation", "description": "Check file exists, readable, not empty"},
    {"stage": "format_detection", "description": "Determine input type (image/PDF/mixed)"},
    {"stage": "grayscale_conversion", "description": "Convert to grayscale for uniform processing"},
    {"stage": "noise_reduction", "description": "Apply median/bilateral filter based on profile"},
    {"stage": "contrast_normalization", "description": "CLAHE or histogram equalization"},
    {"stage": "thresholding", "description": "Otsu's method for binary conversion"},
    {"stage": "deskewing", "description": "Detect and correct rotation angle"},
    {"stage": "resolution_normalization", "description": "Scale to target DPI (150-300)"},
    {"stage": "border_crop", "description": "Remove unnecessary margins"},
]


# =============================================================================
# LANGUAGE PACK ARCHITECTURE
# =============================================================================

LANGUAGE_PACKS = {
    "eng": {"name": "English", "size_mb": 15, "source": "tesseract-data-eng"},
    "fra": {"name": "French", "size_mb": 15, "source": "tesseract-data-fra"},
    "eng_fra": {"name": "English + French", "size_mb": 30, "source": "combined"},
}


if __name__ == "__main__":
    print("OCR Engine Research Report")
    print("=" * 60)
    print(DECISION)
    print("\nEnvironments Constraints:")
    for k, v in ENV_CONSTRAINTS.items():
        print(f"  {k}: {v}")
