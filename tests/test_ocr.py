"""OCR Pipeline Tests — ICON DocForge v1.3

Tests for OCR functionality with graceful degradation when no engine is available.
Uses unittest (no pytest dependency).
"""
import os
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.converters.ocr_pipeline import (
    validate_input,
    preprocess_image,
    run_ocr,
    batch_ocr,
    detect_image_type,
)
from engine.ocr_engine import (
    get_ocr_manager,
    TesseractEngine,
    DummyEngine,
    OCRProfile,
)


class TestInputValidation(unittest.TestCase):
    """Test input validation."""
    
    def test_valid_image_path(self):
        """Test validating a valid image path."""
        result = validate_input("tests/fixtures/ocr/clean_english.png")
        self.assertTrue(result["success"])
        self.assertEqual(result["file_type"], "image")
        self.assertEqual(len(result["errors"]), 0)
    
    def test_valid_pdf_path(self):
        """Test validating a valid PDF path."""
        result = validate_input("tests/fixtures/ocr/multi_page_scan.pdf")
        self.assertTrue(result["success"])
        self.assertEqual(result["file_type"], "pdf")
    
    def test_missing_file(self):
        """Test validating a missing file."""
        result = validate_input("nonexistent.png")
        self.assertFalse(result["success"])
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("not found", result["errors"][0].lower())
    
    def test_unsupported_format(self):
        """Test validating an unsupported format."""
        result = validate_input("tests/fixtures/docx/test_basic.md")
        self.assertFalse(result["success"])
        self.assertIn("unsupported", result["errors"][0].lower())


class TestPreprocessing(unittest.TestCase):
    """Test image preprocessing."""
    
    def test_preprocess_existing_image(self):
        """Test preprocessing an existing image."""
        result = preprocess_image("tests/fixtures/ocr/clean_english.png")
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["output_path"])
        self.assertTrue(os.path.exists(result["output_path"]))
        self.assertEqual(result["profile"], "balanced")


class TestImageTypeDetection(unittest.TestCase):
    """Test image type detection heuristics."""
    
    def test_detect_text_document(self):
        """Test detecting a text document."""
        result = detect_image_type("tests/fixtures/ocr/clean_english.png")
        self.assertIn("is_text_heavy", result)
        self.assertIn("is_scanned", result)
    
    def test_detect_photo(self):
        """Test detecting a photo-like image."""
        # receipt or dark_bg should be detected differently
        result = detect_image_type("tests/fixtures/ocr/dark_bg.png")
        self.assertIn("mean_brightness", result)
        self.assertIn("contrast_level", result)


class TestOCREngine(unittest.TestCase):
    """Test OCR engine abstraction."""
    
    def test_manager_returns_engine(self):
        """Test that manager returns an engine."""
        mgr = get_ocr_manager()
        engine = mgr.get_engine()
        self.assertIsNotNone(engine)
    
    def test_tesseract_not_available(self):
        """Test that TesseractEngine reports not available."""
        is_avail = TesseractEngine.is_available()
        self.assertFalse(is_avail)
    
    def test_dummy_engine_recognition_fails_gracefully(self):
        """Test that dummy engine fails gracefully."""
        engine = DummyEngine()
        result = engine.recognize("tests/fixtures/ocr/clean_english.png")
        
        self.assertFalse(result.success)
        self.assertEqual(result.engine, "dummy")
        self.assertEqual(len(result.errors), 1)
        self.assertIn("no ocr engine", result.errors[0].lower())
    
    def test_ocr_status_command(self):
        """Test the ocr_status method."""
        mgr = get_ocr_manager()
        status = mgr.ocr_status()
        
        self.assertIn("status", status)
        self.assertIn("primary_engine", status)
        self.assertIn("engines", status)
        self.assertIn("recommendations", status)
        
        # Since tesseract not installed, status should be unavailable
        self.assertEqual(status["status"], "unavailable")


class TestOCRPipeline(unittest.TestCase):
    """Test the full OCR pipeline."""
    
    def test_run_ocr_with_missing_engine(self):
        """Test OCR pipeline when engine is missing."""
        result = run_ocr("tests/fixtures/ocr/clean_english.png")
        
        self.assertFalse(result["success"])
        self.assertIn("errors", result)
        self.assertEqual(len(result["errors"]), 1)
    
    def test_run_ocr_with_invalid_input(self):
        """Test OCR pipeline with invalid input."""
        result = run_ocr("nonexistent.png")
        
        self.assertFalse(result["success"])
        self.assertIn("errors", result)
        self.assertIn("not found", result["errors"][0].lower())
    
    def test_batch_ocr_single_file(self):
        """Test batch OCR with single file."""
        result = batch_ocr(["tests/fixtures/ocr/clean_english.png"])
        
        self.assertFalse(result["success"])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["succeeded"], 0)
        self.assertEqual(result["failed"], 1)
    
    def test_ocr_preserves_v12_functionality(self):
        """Test that v1.2 functionality is preserved."""
        # Verify we can still import old converters
        from engine.converters.docx_to_pdf import docx_to_pdf
        from engine.converters.pdf_merge import pdf_merge
        from engine.converters.pdf_split import pdf_split
        
        # These should all be callable without error
        self.assertTrue(callable(docx_to_pdf))
        self.assertTrue(callable(pdf_merge))
        self.assertTrue(callable(pdf_split))


class TestOCRFixtures(unittest.TestCase):
    """Test OCR fixture files."""
    
    def test_fixture_files_exist(self):
        """Test that OCR fixture files exist."""
        fixtures_dir = Path("tests/fixtures/ocr")
        
        self.assertTrue(fixtures_dir.exists(), "OCR fixtures directory does not exist")
        png_files = list(fixtures_dir.glob("*.png"))
        self.assertGreater(len(png_files), 0, "No PNG fixture files found")
    
    def test_fixture_content_readable(self):
        """Test that fixture content can be read."""
        from PIL import Image
        
        fixture = "tests/fixtures/ocr/clean_english.png"
        self.assertTrue(os.path.exists(fixture), f"Fixture not found: {fixture}")
        
        with Image.open(fixture) as img:
            self.assertGreater(img.size[0], 0, "Image width is 0")
            self.assertGreater(img.size[1], 0, "Image height is 0")
    
    def test_all_fixtures_accessible(self):
        """Test that all expected fixtures are accessible."""
        expected = [
            "clean_english.png",
            "clean_french.png",
            "mixed_enfr.png",
            "dark_bg.png",
            "lowres.png",
            "receipt.png",
            "form.png",
            "rotated.png",
            "numbers.png",
            "multi_page_scan.pdf",
        ]
        
        for filename in expected:
            filepath = f"tests/fixtures/ocr/{filename}"
            self.assertTrue(os.path.exists(filepath), f"Missing fixture: {filepath}")


if __name__ == "__main__":
    unittest.main()
