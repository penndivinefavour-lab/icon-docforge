"""OCR Engine Abstraction Layer — ICON DocForge v1.3

Provides a unified interface for OCR engines with graceful degradation
when no engine is available. Supports pluggable backends:
- Tesseract (primary, when available)
- RapidOCR (future, if ARM64 wheels published)
- Mock/Dummy (for testing without engine)
"""
from __future__ import annotations

import os
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple

# Try importing optional dependencies
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None  # type: ignore

try:
    import pytesseract
    HAS_PYTesseract = True
except ImportError:
    HAS_PYTesseract = False
    pytesseract = None  # type: ignore

from engine.utils import safe_run, create_temp_dir, cleanup_temp
from engine.config import OUTPUT_DIR, TEMP_DIR


class OCRProfile(Enum):
    """Processing quality profiles."""
    FAST = "fast"        # Minimal preprocessing, single pass
    BALANCED = "balanced"  # Standard preprocessing
    QUALITY = "quality"  # Aggressive preprocessing, multiple passes


class OCRStatus(Enum):
    """Engine availability status."""
    AVAILABLE = "available"
    PARTIAL = "partial"          # Engine installed but missing languages
    UNAVAILABLE = "unavailable"  # No engine detected


@dataclass
class OCRResult:
    """Result of OCR recognition."""
    success: bool
    text: str = ""
    confidence: float = 0.0
    word_results: List[Dict[str, Any]] = field(default_factory=list)
    pages: int = 1
    engine: str = ""
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OCREngine(ABC):
    """Abstract base class for OCR engines."""
    
    name: str = "unknown"
    version: str = "0.0.0"
    supported_languages: List[str] = []
    has_confidence: bool = False
    has_word_level_confidence: bool = False
    
    @abstractmethod
    def recognize(
        self,
        input_path: str,
        language: str = "eng",
        profile: OCRProfile = OCRProfile.BALANCED,
        force_ocr: bool = False,
        min_confidence: float = 0.0,
    ) -> OCRResult:
        """Run OCR on input (image or PDF)."""
        pass
    
    @abstractmethod
    def detect_language(self, input_path: str) -> str:
        """Auto-detect language from content."""
        pass
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if this engine is installed and usable."""
        return False
    
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        """Return engine metadata."""
        return {
            "name": cls.name,
            "version": cls().version,
            "available": cls.is_available(),
            "languages": cls.supported_languages,
            "confidence": cls.has_confidence,
        }


class TesseractEngine(OCREngine):
    """Tesseract OCR engine wrapper via pytesseract."""
    
    name = "tesseract"
    supported_languages = ["eng", "fra", "deu", "spa", "ara", "chi_sim", "jpn", "kor"]
    has_confidence = True
    has_word_level_confidence = True
    
    _binary: Optional[str] = None
    _instance_version: str = "unknown"
    
    @property
    def version(self) -> str:
        return self._instance_version or "not-installed"
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if tesseract binary is available."""
        if cls._binary is not None:
            return True
        
        # Try common paths
        candidates = [
            "tesseract",
            "/usr/bin/tesseract",
            "/data/data/com.termux/files/usr/bin/tesseract",
        ]
        
        for cmd in candidates:
            result = safe_run([cmd, "--version"], timeout=5)
            if result["success"]:
                cls._binary = cmd
                # Extract version
                import re
                match = re.search(r'version\.?([\d.]+)', result["stdout"])
                if match:
                    cls._instance_version = match.group(1)
                else:
                    cls._instance_version = "installed"
                return True
        
        return False
    
    @property
    def version(self) -> str:
        return self._instance_version or "not-installed"
    
    def recognize(
        self,
        input_path: str,
        language: str = "eng",
        profile: OCRProfile = OCRProfile.BALANCED,
        force_ocr: bool = False,
        min_confidence: float = 0.0,
    ) -> OCRResult:
        """Run Tesseract OCR."""
        if not self.is_available():
            return OCRResult(
                success=False,
                engine="tesseract",
                errors=["Tesseract not installed. Run: pkg install tesseract tesseract-data-eng tesseract-data-fra"],
            )
        
        try:
            import pytesseract
            from PIL import Image
            
            # Open image
            img = Image.open(input_path)
            
            # Preprocess based on profile
            if profile == OCRProfile.FAST:
                img = self._preprocess_fast(img)
            elif profile == OCRProfile.QUALITY:
                img = self._preprocess_quality(img)
            else:
                img = self._preprocess_balanced(img)
            
            # Run OCR
            custom_config = f"--oem 3 --psm 6 lang={language}"
            text = pytesseract.image_to_string(img, lang=language, config=custom_config)
            
            # Get confidence
            data = pytesseract.image_to_data(img, lang=language, config=custom_config, output_type=pytesseract.Output.DICT)
            
            words = []
            total_conf = 0.0
            count = 0
            for i, conf in enumerate(data["conf"]):
                if conf > 0:
                    words.append({
                        "text": data["text"][i],
                        "confidence": float(conf),
                        "bbox": (data["left"][i], data["top"][i], 
                                 data["left"][i] + data["width"][i], 
                                 data["top"][i] + data["height"][i]),
                    })
                    total_conf += conf
                    count += 1
            
            avg_confidence = total_conf / count if count > 0 else 0.0
            
            return OCRResult(
                success=True,
                text=text.strip(),
                confidence=avg_confidence / 100.0,
                word_results=words,
                pages=1,
                engine="tesseract",
            )
            
        except ImportError:
            return OCRResult(
                success=False,
                engine="tesseract",
                errors=["pytesseract not installed. Run: pip install pytesseract"],
            )
        except Exception as e:
            return OCRResult(
                success=False,
                engine="tesseract",
                errors=[str(e)],
            )
    
    def detect_language(self, input_path: str) -> str:
        """Simple language detection (placeholder for now)."""
        return "eng"  # Default until full implementation
    
    def _preprocess_fast(self, img) -> type(img):  # type: ignore[valid-type]
        """Fast preprocessing: grayscale + resize."""
        if img.mode != "L":
            img = img.convert("L")
        # Keep original size for speed
        return img
    
    def _preprocess_balanced(self, img) -> type(img):  # type: ignore[valid-type]
        """Balanced preprocessing."""
        if img.mode != "L":
            img = img.convert("L")
        # Apply mild sharpening
        from PIL import ImageFilter
        img = img.filter(ImageFilter.SHARPEN)
        return img
    
    def _preprocess_quality(self, img) -> type(img):  # type: ignore[valid-type]
        """Quality preprocessing: denoise + enhance + threshold."""
        if img.mode != "L":
            img = img.convert("L")
        
        from PIL import ImageEnhance, ImageFilter
        
        # Denoise
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Sharpen
        img = img.filter(ImageFilter.SHARPEN)
        
        return img


class DummyEngine(OCREngine):
    """Dummy engine for testing without real OCR."""
    
    name = "dummy"
    version = "test"
    supported_languages = ["eng", "fra"]
    has_confidence = False
    
    def recognize(self, input_path, language="eng", profile=OCRProfile.BALANCED, 
                  force_ocr=False, min_confidence=0.0) -> OCRResult:
        return OCRResult(
            success=False,
            engine="dummy",
            errors=["No OCR engine available. Install tesseract via: pkg install tesseract tesseract-data-eng tesseract-data-fra"],
        )
    
    def detect_language(self, input_path: str) -> str:
        return "eng"


class OCRManager:
    """Manages OCR engine selection and execution."""
    
    def __init__(self):
        self._engine_cache: Dict[str, OCREngine] = {}
        self._active_engine: Optional[OCREngine] = None
    
    def get_engine(self, name: str = "auto") -> OCREngine:
        """Get the best available engine."""
        if name == "auto":
            # Try tesseract first, then dummy
            if TesseractEngine.is_available():
                return TesseractEngine()
            return DummyEngine()
        
        if name == "tesseract":
            return TesseractEngine()
        
        if name == "dummy":
            return DummyEngine()
        
        raise ValueError(f"Unknown OCR engine: {name}")
    
    def ocr_status(self) -> Dict[str, Any]:
        """Get comprehensive OCR status."""
        engines = {
            "tesseract": TesseractEngine(),
            "dummy": DummyEngine(),
        }
        
        results = {}
        for name, engine in engines.items():
            info = engine.get_info()
            info["available"] = engine.is_available()
            results[name] = info
        
        # Determine overall status
        if TesseractEngine.is_available():
            overall = OCRStatus.AVAILABLE
            primary = "tesseract"
        else:
            overall = OCRStatus.UNAVAILABLE
            primary = "none"
        
        return {
            "status": overall.value,
            "primary_engine": primary,
            "engines": results,
            "languages": TesseractEngine.supported_languages if TesseractEngine.is_available() else [],
            "recommendations": self._get_recommendations(),
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations for improving OCR capability."""
        recs = []
        
        if not TesseractEngine.is_available():
            recs.append("Install Tesseract: pkg install tesseract tesseract-data-eng tesseract-data-fra")
            recs.append("Then restart the application")
        
        return recs
    
    def run_ocr(
        self,
        input_path: str,
        output_format: str = "txt",
        language: str = "eng",
        profile: str = "balanced",
        force_ocr: bool = False,
        min_confidence: float = 0.0,
    ) -> OCRResult:
        """Run OCR with selected engine."""
        engine = self.get_engine()
        profile_enum = OCRProfile(profile)
        
        result = engine.recognize(
            input_path=input_path,
            language=language,
            profile=profile_enum,
            force_ocr=force_ocr,
            min_confidence=min_confidence,
        )
        
        result.output_format = output_format
        return result


# Singleton instance
_ocr_manager: Optional[OCRManager] = None

def get_ocr_manager() -> OCRManager:
    global _ocr_manager
    if _ocr_manager is None:
        _ocr_manager = OCRManager()
    return _ocr_manager


# CLI helper functions
def ocr_command(input_path: str, output_path: str = None, 
                output_format: str = "txt", language: str = "eng",
                profile: str = "balanced", force_ocr: bool = False) -> dict:
    """CLI entry point for OCR operations."""
    mgr = get_ocr_manager()
    result = mgr.run_ocr(
        input_path=input_path,
        output_format=output_format,
        language=language,
        profile=profile,
        force_ocr=force_ocr,
    )
    
    # Write output
    if result.success and output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.text)
    
    return {
        "success": result.success,
        "output": output_path or result.text[:200],
        "confidence": result.confidence,
        "engine": result.engine,
        "errors": result.errors,
    }


def ocr_status_command() -> dict:
    """CLI entry point for status checks."""
    return get_ocr_manager().ocr_status()


if __name__ == "__main__":
    # Self-test
    print("OCR Engine Self-Test")
    print("=" * 50)
    
    mgr = get_ocr_manager()
    status = mgr.ocr_status()
    
    print(f"Status: {status['status']}")
    print(f"Primary engine: {status['primary_engine']}")
    print()
    
    for name, info in status["engines"].items():
        avail = "✅" if info["available"] else "❌"
        print(f"{avail} {name}: {info['version']}")
    
    print()
    if status["recommendations"]:
        print("Recommendations:")
        for rec in status["recommendations"]:
            print(f"  • {rec}")
