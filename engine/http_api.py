"""Local HTTP API for ICON DocForge conversion engine.

Binds to 127.0.0.1:8765 by default. Provides:
- POST /convert - Convert documents
- POST /images-to-pdf - Convert images to PDF
- POST /pdf-merge - Merge PDFs
- POST /pdf-split - Split a PDF
- GET /formats - List supported formats
- GET /health - Health check
- GET /report - Full engine report
"""

import os
import sys
import json
import threading
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from engine.registry import get_registry
from engine.utils import safe_run, TempDirectory, validate_input_file, validate_output_path, format_size, get_resource_manager
from engine.config import HTTP_HOST, HTTP_PORT, HTTP_MAX_CONTENT_LENGTH, BINARIES, DEFAULT_TIMEOUT, OUTPUT_DIR, MAX_INPUT_SIZE_BYTES

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = HTTP_MAX_CONTENT_LENGTH

registry = get_registry()


# ── Helper functions ──────────────────────────────────────────────

def _json_error(message: str, status_code: int = 400) -> tuple:
    """Create a JSON error response."""
    return jsonify({"error": message, "status": "error"}), status_code


def _json_success(data: dict, status_code: int = 200) -> tuple:
    """Create a JSON success response."""
    return jsonify({"status": "success", "data": data}), status_code


def _validate_files(file_list: list, min_count: int = 1) -> list[Path]:
    """Validate a list of file paths."""
    paths = []
    for f in file_list:
        try:
            p = validate_input_file(f)
            paths.append(p)
        except (FileNotFoundError, PermissionError) as e:
            raise ValueError(str(e))
    if len(paths) < min_count:
        raise ValueError(f"At least {min_count} file(s) required")
    return paths


# ── Routes ────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    health = registry.health_check()
    summary = health.get("_summary", {})
    healthy = summary.get("overall_health") == "healthy"
    return jsonify({
        "status": "healthy" if healthy else "degraded",
        "engine": "ICON DocForge",
        "version": "1.0.0",
        **summary
    }), 200 if healthy else 503


@app.route("/report", methods=["GET"])
def report():
    """Get full engine capability report."""
    report_data = registry.get_report()
    return jsonify({
        "status": "success",
        "data": {
            "engine_name": report_data.engine_name,
            "engine_version": report_data.engine_version,
            "total_converters": report_data.total_converters,
            "healthy_converters": report_data.healthy_converters,
            "overall_health": report_data.overall_health,
            "converters": [
                {
                    "name": c.name,
                    "display_name": c.display_name,
                    "description": c.description,
                    "installed": c.installed,
                    "version": c.version,
                    "input_formats": c.input_formats,
                    "output_formats": c.output_formats,
                    "health": c.health,
                    "error": c.error,
                }
                for c in report_data.converters
            ],
            "binaries": {k: v for k, v in report_data.binaries_found.items()},
            "max_input_size": report_data.max_input_size,
            "max_output_size": report_data.max_output_size,
            "default_timeout": report_data.default_timeout,
        }
    })


@app.route("/formats", methods=["GET"])
def formats():
    """List supported formats and converters."""
    converters = registry.get_all_converters()
    return jsonify({
        "status": "success",
        "data": {
            "converters": [
                {
                    "name": c.name,
                    "display_name": c.display_name,
                    "input_formats": c.input_formats,
                    "output_formats": c.output_formats,
                    "installed": c.installed,
                }
                for c in converters
            ]
        }
    })


@app.route("/convert", methods=["POST"])
def convert():
    """Convert a document file to a target format.

    JSON body:
    {
        "input": "/path/to/file.docx",
        "to": "pdf",
        "output": "/path/to/output.pdf"  (optional)
    }
    """
    data = request.get_json(force=True)
    if not data or "input" not in data or "to" not in data:
        return _json_error("Missing 'input' and 'to' fields", 400)

    input_path = data["input"]
    target_format = data["to"].lower().strip()
    output_path = data.get("output")

    try:
        inp = validate_input_file(input_path)
    except (FileNotFoundError, PermissionError, ValueError) as e:
        return _json_error(str(e), 404)

    if not output_path:
        output_path = str(Path(inp.parent / f"{inp.stem}.{target_format}"))

    try:
        out = validate_output_path(output_path)
    except PermissionError as e:
        return _json_error(str(e), 403)

    # Route conversion
    input_ext = inp.suffix.lower()
    try:
        if input_ext == ".docx" and target_format == "pdf":
            return _handle_docx_to_pdf(inp, out)
        elif input_ext == ".md" and target_format == "pdf":
            return _handle_markdown_to_pdf(inp, out)
        else:
            return _json_error(f"Conversion {input_ext} → {target_format} not supported", 400)
    except Exception as e:
        return _json_error(f"Conversion failed: {str(e)}", 500)


@app.route("/images-to-pdf", methods=["POST"])
def images_to_pdf():
    """Convert images to PDF.

    JSON body:
    {
        "images": ["/path/to/img1.jpg", "/path/to/img2.png"],
        "output": "/path/to/result.pdf"
    }
    """
    data = request.get_json(force=True)
    if not data or "images" not in data or "output" not in data:
        return _json_error("Missing 'images' or 'output' fields", 400)

    try:
        paths = _validate_files(data["images"])
        out = validate_output_path(data["output"])
    except ValueError as e:
        return _json_error(str(e), 400)

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
        from PIL import Image as PILImage

        c = canvas.Canvas(str(out), pagesize=A4)
        width, height = A4

        for i, img_path in enumerate(paths):
            img = PILImage.open(img_path)
            img_w, img_h = img.size
            scale = min(width / img_w, height / img_h) * 0.9
            new_w = img_w * scale
            new_h = img_h * scale
            x = (width - new_w) / 2
            y = (height - new_h) / 2
            c.drawImage(ImageReader(str(img_path)), x, y, width=new_w, height=new_h)
            if i < len(paths) - 1:
                c.showPage()
        c.save()

        size = out.stat().st_size
        return _json_success({
            "output": str(out),
            "size": size,
            "size_human": format_size(size),
            "pages": len(paths)
        })
    except Exception as e:
        return _json_error(f"Image-to-PDF conversion failed: {str(e)}", 500)


@app.route("/pdf-merge", methods=["POST"])
def pdf_merge():
    """Merge multiple PDFs.

    JSON body:
    {
        "pdfs": ["/path/a.pdf", "/path/b.pdf"],
        "output": "/path/merged.pdf"
    }
    """
    data = request.get_json(force=True)
    if not data or "pdfs" not in data or "output" not in data:
        return _json_error("Missing 'pdfs' or 'output' fields", 400)

    try:
        paths = _validate_files(data["pdfs"], min_count=2)
        out = validate_output_path(data["output"])
    except ValueError as e:
        return _json_error(str(e), 400)

    pdfunite = BINARIES.get("pdfunite")
    if not pdfunite:
        return _json_error("pdfunite not found", 501)

    result = safe_run(
        [pdfunite] + [str(p.resolve()) for p in paths] + [str(out.resolve())],
        timeout=DEFAULT_TIMEOUT,
    )

    if result.success and out.exists():
        size = out.stat().st_size
        return _json_success({
            "output": str(out),
            "size": size,
            "size_human": format_size(size),
            "merged": len(paths)
        })
    return _json_error(result.error or "Merge failed", 500)


@app.route("/pdf-split", methods=["POST"])
def pdf_split():
    """Split a PDF into page ranges.

    JSON body:
    {
        "input": "/path/input.pdf",
        "pages": "1-3",
        "output": "/path/output.pdf"
    }
    """
    data = request.get_json(force=True)
    if not data or "input" not in data or "pages" not in data or "output" not in data:
        return _json_error("Missing 'input', 'pages', or 'output' fields", 400)

    try:
        inp = validate_input_file(data["input"])
        out = validate_output_path(data["output"])
    except (FileNotFoundError, PermissionError) as e:
        return _json_error(str(e), 400)

    pdfseparate = BINARIES.get("pdfseparate")
    if not pdfseparate:
        return _json_error("pdfseparate not found", 501)

    pages_spec = data["pages"]
    try:
        if "-" in pages_spec:
            start, end = pages_spec.split("-", 1)
            start, end = int(start), int(end)
        else:
            start = end = int(pages_spec)
    except ValueError:
        return _json_error(f"Invalid page range '{pages_spec}'", 400)

    from engine.utils import TempDirectory
    import shutil

    with TempDirectory(prefix="pdf-split-api-") as tmpdir:
        result = safe_run(
            [pdfseparate, str(inp.resolve()), str(tmpdir / "page"), "-f", str(start), "-l", str(end)],
            timeout=DEFAULT_TIMEOUT,
        )
        if not result.success:
            return _json_error(result.error or "Split failed", 500)

        page_files = sorted(tmpdir.glob("page-*.pdf"))
        if not page_files:
            return _json_error("No pages extracted", 404)

        if len(page_files) > 1:
            pdfunite = BINARIES.get("pdfunite")
            if pdfunite:
                result = safe_run(
                    [pdfunite] + [str(f) for f in page_files] + [str(out.resolve())],
                    timeout=DEFAULT_TIMEOUT,
                )
                if result.success and out.exists():
                    size = out.stat().st_size
                    return _json_success({"output": str(out), "size": size, "size_human": format_size(size)})
            shutil.copy2(page_files[0], out)
        elif len(page_files) == 1:
            shutil.copy2(page_files[0], out)

        size = out.stat().st_size
        return _json_success({"output": str(out), "size": size, "size_human": format_size(size)})


@app.route("/docx-to-pdf", methods=["POST"])
def docx_to_pdf():
    """Convert DOCX to PDF.

    JSON body:
    {
        "input": "/path/document.docx",
        "output": "/path/document.pdf"  (optional)
    }
    """
    data = request.get_json(force=True)
    if not data or "input" not in data:
        return _json_error("Missing 'input' field", 400)

    input_path = data["input"]
    output_path = data.get("output")

    try:
        inp = validate_input_file(input_path)
    except (FileNotFoundError, PermissionError) as e:
        return _json_error(str(e), 404)

    if not output_path:
        output_path = str(Path(inp.parent / f"{inp.stem}.pdf"))

    try:
        out = validate_output_path(output_path)
    except PermissionError as e:
        return _json_error(str(e), 403)

    return _handle_docx_to_pdf(inp, out)


def _handle_docx_to_pdf(input_path: Path, output_path: Path) -> tuple:
    """Handle DOCX to PDF conversion."""
    pandoc = BINARIES.get("pandoc")
    weasyprint = BINARIES.get("weasyprint")

    if not pandoc:
        return _json_error("pandoc not found", 501)

    with TempDirectory(prefix="docx2pdf-api-") as tmpdir:
        result = safe_run([pandoc, str(input_path), "-o", str(output_path)], timeout=DEFAULT_TIMEOUT)
        if result.success and output_path.exists():
            size = output_path.stat().st_size
            return _json_success({"output": str(output_path), "size": size, "size_human": format_size(size)})

        # Fallback via HTML
        if pandoc and weasyprint:
            html_path = tmpdir / "intermediate.html"
            r1 = safe_run([pandoc, str(input_path), "-o", str(html_path)], timeout=DEFAULT_TIMEOUT)
            if r1.success:
                r2 = safe_run([weasyprint, str(html_path), str(output_path)], timeout=DEFAULT_TIMEOUT)
                if r2.success and output_path.exists():
                    size = output_path.stat().st_size
                    return _json_success({"output": str(output_path), "size": size, "size_human": format_size(size)})

        return _json_error(result.error or "Conversion failed", 500)


@app.route("/markdown-to-pdf", methods=["POST"])
def markdown_to_pdf():
    """Convert Markdown to PDF."""
    data = request.get_json(force=True)
    if not data or "input" not in data:
        return _json_error("Missing 'input' field", 400)

    input_path = data["input"]
    output_path = data.get("output")

    try:
        inp = validate_input_file(input_path)
    except (FileNotFoundError, PermissionError) as e:
        return _json_error(str(e), 404)

    if not output_path:
        output_path = str(Path(inp.parent / f"{inp.stem}.pdf"))

    try:
        out = validate_output_path(output_path)
    except PermissionError as e:
        return _json_error(str(e), 403)

    pandoc = BINARIES.get("pandoc")
    if not pandoc:
        return _json_error("pandoc not found", 501)

    result = safe_run([pandoc, str(inp), "-o", str(out)], timeout=DEFAULT_TIMEOUT)
    if result.success and out.exists():
        size = out.stat().st_size
        return _json_success({"output": str(out), "size": size, "size_human": format_size(size)})
    return _json_error(result.error or "Conversion failed", 500)


# ── Server runner ─────────────────────────────────────────────────

def run_server(host: str = None, port: int = None, debug: bool = False) -> None:
    """Start the HTTP server."""
    host = host or HTTP_HOST
    port = port or HTTP_PORT
    print(f"ICON DocForge API starting on http://{host}:{port}")
    print(f"Health:  http://{host}:{port}/health")
    print(f"Report:  http://{host}:{port}/report")
    print(f"Formats: http://{host}:{port}/formats")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    run_server()
