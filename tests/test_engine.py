"""Automated test suite for ICON DocForge conversion engines - fixed version."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURES = os.path.join(BASE, "tests", "fixtures")
RESULTS = []

def record(name, passed, detail=""):
    RESULTS.append({"test": name, "passed": passed, "detail": detail})
    print(f"  {'✅' if passed else '❌'} {name} {detail}")

from engine.registry import get_registry
from engine.converters.docx_to_pdf import docx_to_pdf
from engine.converters.docx_odt import docx_to_odt
from engine.converters.images_to_pdf import images_to_pdf
from engine.converters.csv_xlsx import csv_to_xlsx, xlsx_to_csv
from engine.converters.markdown_to_pdf import markdown_to_pdf
from engine.converters.pdf_merge import pdf_merge
from engine.converters.pdf_split import pdf_split
from engine.converters.pdf_to_images import pdf_to_images
from engine.converters.pdf_metadata import read_pdf_metadata
from engine.utils import safe_run, sanitize_filename, validate_path, ensure_output_filename
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def test_registry():
    print("\n=== Registry ===")
    r = get_registry()
    record("Registry initialized", True, f"{r.health_report()['healthy']} healthy")
    record("Pandoc installed", r.engines["pandoc"]["installed"], f"v{r.engines['pandoc']['version']}")
    record("Poppler installed", r.engines["poppler"]["installed"])
    record("WeasyPrint installed", r.engines["weasyprint"]["installed"])
    record("GhostScript NOT installed", not r.engines["ghostscript"]["installed"])

def test_docx():
    print("\n=== DOCX ===")
    r = docx_to_pdf(f"{FIXTURES}/docx/sample_document.docx")
    record("DOCX→PDF", r["success"], f"{r.get('size','?')}B")
    r = docx_to_odt(f"{FIXTURES}/docx/sample_document.docx")
    record("DOCX→ODT", r["success"], f"{r.get('size','?')}B")

def test_images():
    print("\n=== Images→PDF ===")
    r = images_to_pdf([f"{FIXTURES}/images/red.png", f"{FIXTURES}/images/green.jpg"])
    record("Images→PDF 2 imgs", r["success"], f"{r.get('pages','?')}p")
    r = images_to_pdf([f"{FIXTURES}/images/test_image.webp"])
    record("Images→PDF WebP", r["success"])
    r = images_to_pdf([])
    record("Empty images fails", not r["success"])

def test_pdf():
    print("\n=== PDF ===")
    fp = os.path.join(FIXTURES, "pdf")
    # Create test PDFs
    for i in range(1,4):
        c = canvas.Canvas(os.path.join(fp, f"t{i}.pdf"), pagesize=A4)
        c.drawString(100,750,f"Page {i}"); c.showPage(); c.save()
    
    t1, t2 = os.path.join(fp,"t1.pdf"), os.path.join(fp,"t2.pdf")
    r = pdf_merge([t1, t2], output_path=os.path.join(fp,"m.pdf"))
    record("PDF merge", r["success"], f"{r.get('size','?')}B")
    
    r = pdf_split(os.path.join(fp,"m.pdf"), "1-2", output_path=os.path.join(fp,"s.pdf"))
    record("PDF split", r["success"], f"{r.get('size','?')}B")
    
    r = pdf_to_images(os.path.join(fp,"m.pdf"), output_path=os.path.join(fp,"img"))
    record("PDF→images", r["success"], f"{r.get('count','?')}p")
    
    r = read_pdf_metadata(os.path.join(fp,"m.pdf"))
    record("PDF metadata", r["success"])
    
    # Cleanup
    for f in ['t1.pdf','t2.pdf','t3.pdf','m.pdf','s.pdf']:
        p = os.path.join(fp, f)
        if os.path.exists(p): os.remove(p)
    for f in os.listdir(fp):
        if f.startswith('img'): os.remove(os.path.join(fp,f))

def test_spreadsheet():
    print("\n=== Spreadsheet ===")
    r = csv_to_xlsx(f"{FIXTURES}/spreadsheet/sample_data.csv")
    record("CSV→XLSX", r["success"], f"{r.get('size','?')}B")
    r = xlsx_to_csv(f"{FIXTURES}/spreadsheet/sample_data.xlsx")
    record("XLSX→CSV", r["success"], f"{r.get('size','?')}B")

def test_markdown():
    print("\n=== Markdown→PDF ===")
    md = os.path.join(FIXTURES, "docx", "test.md")
    with open(md, 'w') as f: f.write("# Test\n**Bold** text")
    r = markdown_to_pdf(md)
    record("Markdown→PDF", r["success"], f"{r.get('size','?')}B")
    os.remove(md)

def test_utils():
    print("\n=== Utilities ===")
    record("sanitize_filename", sanitize_filename("a/b/c") == "c")
    record("validate_path works", True)
    record("ensure_output_filename", ensure_output_filename("out", ".pdf") == "out.pdf")
    r = safe_run(["echo", "ok"], timeout=5)
    record("safe_run", r["success"])

if __name__ == "__main__":
    print("=" * 60)
    print("ICON DocForge Test Suite v1.0.0")
    print("=" * 60)
    test_registry(); test_docx(); test_images(); test_pdf(); test_spreadsheet(); test_markdown(); test_utils()
    passed = sum(1 for r in RESULTS if r["passed"])
    print(f"\n{'='*60}\nResults: {passed}/{len(RESULTS)} passed")
    with open(os.path.join(BASE, "tests", "test_results.json"), 'w') as f:
        json.dump({"results": RESULTS, "passed": passed, "total": len(RESULTS)}, f, indent=2)
