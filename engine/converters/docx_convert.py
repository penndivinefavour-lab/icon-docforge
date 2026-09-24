"""DOCX ↔ HTML/TXT/MD/ODT converters using pandoc."""
import os
from engine.utils import safe_run
from engine.config import OUTPUT_DIR


def docx_to_html(input_path: str, output_path: str = None, standalone: bool = True) -> dict:
    """Convert DOCX to standalone HTML."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "DOCX not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".html")
    args = ["pandoc", input_path, "-t", "html5"]
    if standalone:
        args.append("-s")
    args += ["-o", output_path, "--self-contained"]
    result = safe_run(args, timeout=60)
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc", "fidelity": "HIGH-FIDELITY"}
    return {"success": False, "error": result.get("stderr", "Conversion failed")[:300]}


def html_to_docx(input_path: str, output_path: str = None) -> dict:
    """Convert HTML to DOCX."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "HTML not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".docx")
    result = safe_run(["pandoc", input_path, "-f", "html", "-t", "docx", "-o", output_path], timeout=60)
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc", "fidelity": "HIGH-FIDELITY"}
    return {"success": False, "error": result.get("stderr", "Conversion failed")[:300]}


def docx_to_txt(input_path: str, output_path: str = None) -> dict:
    """Convert DOCX to plain text using docx2txt."""
    import docx2txt
    if not os.path.exists(input_path):
        return {"success": False, "error": "DOCX not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".txt")
    try:
        text = docx2txt.process(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "docx2txt", "fidelity": "HIGH-FIDELITY"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def txt_to_docx(input_path: str, output_path: str = None) -> dict:
    """Convert plain text to DOCX."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "TXT not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".docx")
    result = safe_run(["pandoc", input_path, "-t", "docx", "-o", output_path], timeout=30)
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc", "fidelity": "HIGH-FIDELITY"}
    return {"success": False, "error": result.get("stderr", "Conversion failed")[:300]}


def docx_to_markdown(input_path: str, output_path: str = None) -> dict:
    """Convert DOCX to Markdown."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "DOCX not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".md")
    result = safe_run(["pandoc", input_path, "-t", "gfm", "-o", output_path], timeout=30)
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc", "fidelity": "HIGH-FIDELITY"}
    return {"success": False, "error": result.get("stderr", "Conversion failed")[:300]}


def markdown_to_docx(input_path: str, output_path: str = None) -> dict:
    """Convert Markdown to DOCX."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "Markdown not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".docx")
    result = safe_run(["pandoc", input_path, "-f", "gfm", "-t", "docx", "-o", output_path], timeout=30)
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc", "fidelity": "HIGH-FIDELITY"}
    return {"success": False, "error": result.get("stderr", "Conversion failed")[:300]}


def docx_to_epub(input_path: str, output_path: str = None) -> dict:
    """Convert DOCX to EPUB."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "DOCX not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".epub")
    result = safe_run(["pandoc", input_path, "-t", "epub", "-o", output_path, "--metadata=title:ICON DocForge Export"], timeout=60)
    if result["success"] and os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "pandoc", "fidelity": "HIGH-FIDELITY"}
    return {"success": False, "error": result.get("stderr", "Conversion failed")[:300]}


def html_to_pdf(input_path: str, output_path: str = None) -> dict:
    """Convert HTML to PDF using weasyprint."""
    from weasyprint import HTML
    if not os.path.exists(input_path):
        return {"success": False, "error": "HTML not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    try:
        HTML(filename=input_path).write_pdf(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return {"success": True, "output": output_path, "size": os.path.getsize(output_path), "method": "weasyprint", "fidelity": "HIGH-FIDELITY"}
        return {"success": False, "error": "Output PDF not created"}
    except Exception as e:
        return {"success": False, "error": str(e)}
