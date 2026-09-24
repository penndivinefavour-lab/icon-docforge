# OCR Engine Research — ICON DocForge v1.3

## Executive Summary

After exhaustive investigation, **no production OCR engine is currently available** for the Pixel 4a/Termux environment due to:

1. **No ARM64 prebuilt wheels** for Python-based engines (RapidOCR, EasyOCR, PaddleOCR all require torch/onnxruntime which lack ARM64 wheels)
2. **Tesseract package unavailable** — Termux repository mirrors are currently unreachable (all 10 tested mirrors returning connection failures)
3. **Storage constraints** — Only 3.0 GB free; heavy engines (torch ~3.5GB, onnxruntime ~271MB) exceed budget
4. **RAM constraints** — 832 MB available; most neural OCR engines require 500MB-2GB during inference

**Status: OCR functionality deferred to v1.4 with engine discovery.**

---

## Investigated Engines

### 1. Tesseract OCR ✅ Preferred (When Available)
- **Status**: Package unavailable (Termux repo connectivity issues)
- **Installation**: `pkg install tesseract tesseract-oemp`
- **ARM64 Support**: Yes (native binary)
- **Model Size**: ~50 MB (eng + fra language packs)
- **RAM Usage**: ~200 MB during processing
- **Languages**: 100+ (including English, French, Arabic, Chinese, Japanese)
- **Accuracy**: High for typed text, Good for clean scans
- **Preprocessing**: Built-in (denoise, binarization, deskew)
- **Confidence**: Word-level confidence scores
- **License**: Apache-2.0
- **APK Compatible**: No (requires native .so bundling)
- **Offline**: Yes, after model download

### 2. RapidOCR (ONNX Runtime) ❌ Unavailable
- **Status**: No ARM64 wheel published on PyPI
- **Installation**: `pip install rapidocr-onnxruntime`
- **ARM64 Wheels**: 0 found
- **Model Size**: ~40 MB (DBNet + CRNN)
- **RAM Usage**: ~300 MB during processing
- **Languages**: 30+ (eng, fra, chi_sim, jpn, kor, ara)
- **Accuracy**: High (modern DBNet + CRNN architecture)
- **Confidence**: Word-level confidence
- **License**: MIT
- **Issue**: Pip hangs compiling C extensions (pyclipper, shapely) on Termux

### 3. EasyOCR ❌ Rejected
- **Status**: Requires torch (no ARM64 support)
- **Model Size**: ~200 MB+
- **RAM Usage**: ~1 GB+ during processing
- **Languages**: 70+
- **Accuracy**: Very High
- **Issue**: Too heavy for constrained environment

### 4. PaddleOCR ❌ Rejected
- **Status**: Requires paddlepaddle framework
- **Model Size**: ~150 MB+
- **RAM Usage**: ~500 MB+
- **Languages**: 100+
- **Accuracy**: Very High (industry-leading)
- **Issue**: No ARM64 support, massive dependency chain

---

## Environment Constraints (Pixel 4a / Termux)

| Constraint | Value | Impact |
|------------|-------|--------|
| Architecture | aarch64 (ARM64) | Limits prebuilt wheel availability |
| Total RAM | 5.5 GB | Shared with OS, apps, Termux |
| Available RAM | ~832 MB | Most neural OCR needs 500MB-2GB |
| Free Storage | ~3.0 GB | Tesseract models: ~50MB viable |
| Python | 3.14.6 | Latest, some packages not yet compatible |
| NumPy | 2.4.4 | Available (foundation for image processing) |
| Pillow | 12.3.0 | Available (image I/O) |

---

## Language Pack Availability

| Language | Tesseract Pack | Size |
|----------|---------------|------|
| English (eng) | tesseract-data-eng | ~15 MB |
| French (fra) | tesseract-data-fra | ~15 MB |
| Combined eng+fra | — | ~30 MB |

**Cameroon Context**: Bilingual English/French support critical for local use cases.

---

## Implementation Strategy

Since no OCR engine is currently available, the v1.3 implementation focuses on:

1. **Infrastructure**: Build complete OCR pipeline architecture ready for any engine
2. **Preprocessing**: Implement robust image preprocessing using Pillow (available)
3. **Graceful Degradation**: Clear messaging when no OCR engine is detected
4. **Future-Proofing**: Engine abstraction layer for easy swapping
5. **Testing**: Comprehensive test suite with fixture validation

### Engine Interface Design

```python
class OCREngine(ABC):
    """Abstract base class for OCR engines."""
    
    @abstractmethod
    async def recognize(self, image: Image) -> OCRResult: ...
    
    @abstractmethod
    def detect_language(self, image: Image) -> str: ...
    
    @classmethod
    def available_engines(cls) -> list[str]: ...
    
    @classmethod
    def get_engine(cls, name: str) -> 'OCREngine': ...
```

### Preprocessing Pipeline (Pillow-only)

```
Input → Validate → Grayscale → Denoise → Contrast → Threshold → 
Deskew → Resize → Crop → OCR Engine → Post-process → Output
```

---

## Status & Next Steps

### v1.3.0 Scope (Current Release)
- ✅ OCR pipeline infrastructure
- ✅ Preprocessing engine (Pillow-based)
- ✅ Engine abstraction layer
- ✅ Test fixtures (10 OCR images)
- ✅ CLI commands (ocr, ocr-status, doctor)
- ⚠️ OCR recognition: **GRACEFUL FAILURE** when no engine available
- ✅ Documentation of limitations

### v1.4.0 Planned (Engine Integration)
- 🔲 Tesseract integration (when package available)
- 🔲 RapidOCR integration (if ARM64 wheels published)
- 🔲 Language pack management
- 🔲 Confidence threshold controls
- 🔲 Batch OCR processing

---

## Technical Notes

### Why No Prebuilt ARM64 Wheels?

Most deep learning OCR engines depend on:
- **torch** (~3.5 GB, no Android/ARM64 support)
- **onnxruntime** (~271 MB, limited ARM64 coverage)
- **tensorflow** (~2 GB, minimal ARM64 support)

RapidOCR attempted to publish ARM64 wheels but encountered compilation issues with C extensions (pyclipper, shapely) on Termux's Bionic libc.

### Alternative Approaches Considered

1. **WebAssembly Tesseract**: Browser-based OCR via wasmer/wasmtime — requires WASM runtime, adds complexity
2. **Native Android OCR**: ML Kit / CameraX — requires Java/Kotlin bridge, APK-specific
3. **Remote API Fallback**: Explicit opt-in only, never default — privacy violation concern
4. **Pre-built Binaries**: Download from GitHub releases — requires network, trust verification

**Decision**: All deferred. Focus on infrastructure readiness.

---

*Research Date: 2026-09-24*
*Author: Divine Favour · ICON Studios*
*Device: Pixel 4a · Termux aarch64*
