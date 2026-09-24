"""CLI interface for ICON DocForge v1.1."""
import sys
import os
import argparse
import json

def main():
    parser = argparse.ArgumentParser(
        prog="iconconvert",
        description="ICON DocForge v1.1 - Offline-first document conversion CLI"
    )
    sub = parser.add_subparsers(dest="command")
    
    # convert command
    p = sub.add_parser("convert", help="Convert a file")
    p.add_argument("input", help="Input file path")
    p.add_argument("--to", required=True, help="Output format (pdf, docx, odt, html, txt, md)")
    p.add_argument("--output", help="Output file path")
    
    # images-to-pdf
    p = sub.add_parser("images-to-pdf", help="Convert images to PDF")
    p.add_argument("images", nargs="+", help="Image files")
    p.add_argument("--output", help="Output PDF path")
    p.add_argument("--page-size", default="A4", help="Page size (A4, Letter)")
    p.add_argument("--orientation", default="portrait", help="Orientation")
    p.add_argument("--quality", type=int, default=85, help="Image quality")
    
    # pdf-merge
    p = sub.add_parser("pdf-merge", help="Merge PDFs")
    p.add_argument("pdfs", nargs="+", help="PDF files to merge")
    p.add_argument("--output", help="Output PDF path")
    
    # pdf-split
    p = sub.add_parser("pdf-split", help="Split a PDF")
    p.add_argument("input", help="Input PDF")
    p.add_argument("--pages", required=True, help="Page range (e.g., 1-3)")
    p.add_argument("--output", help="Output PDF path")
    
    # pdf-to-images
    p = sub.add_parser("pdf-to-images", help="Convert PDF to images")
    p.add_argument("input", help="Input PDF")
    p.add_argument("--output", help="Output prefix")
    p.add_argument("--format", default="png", help="Image format")
    p.add_argument("--dpi", type=int, default=150, help="DPI")
    
    # pdf-text
    p = sub.add_parser("pdf-text", help="Extract text from PDF")
    p.add_argument("input", help="Input PDF")
    p.add_argument("--output", help="Output text file")
    
    # pdf-search
    p = sub.add_parser("pdf-search", help="Search text in PDF")
    p.add_argument("input", help="Input PDF")
    p.add_argument("query", help="Search query")
    p.add_argument("--case-sensitive", action="store_true", help="Case sensitive search")
    
    # pdf-info
    p = sub.add_parser("pdf-info", help="Get PDF page information")
    p.add_argument("input", help="Input PDF")
    
    # pdf-compress
    p = sub.add_parser("pdf-compress", help="Compress PDF")
    p.add_argument("input", help="Input PDF")
    p.add_argument("--output", help="Output PDF path")
    p.add_argument("--dpi", type=int, default=72, help="DPI (lower = smaller)")
    
    # pdf-watermark
    p = sub.add_parser("pdf-watermark", help="Add text watermark to PDF")
    p.add_argument("input", help="Input PDF")
    p.add_argument("--text", default="CONFIDENTIAL", help="Watermark text")
    p.add_argument("--output", help="Output PDF path")
    
    # pdf-reorder
    p = sub.add_parser("pdf-reorder", help="Reorder PDF pages")
    p.add_argument("input", help="Input PDF")
    p.add_argument("--pages", required=True, help="Page order (comma-separated, e.g., 3,1,2)")
    p.add_argument("--output", help="Output PDF path")
    
    # pdf-delete
    p = sub.add_parser("pdf-delete", help="Delete pages from PDF")
    p.add_argument("input", help="Input PDF")
    p.add_argument("--pages", required=True, help="Pages to delete (comma-separated, e.g., 1,3,5)")
    p.add_argument("--output", help="Output PDF path")
    
    # doctor
    sub.add_parser("doctor", help="Check engine health")
    
    # formats
    sub.add_parser("formats", help="List supported formats")
    
    # office-status
    p = sub.add_parser("office-status", help="Diagnose Office conversion support")
    
    # ocr
    p = sub.add_parser("ocr", help="Run OCR on an image or PDF")
    p.add_argument("input", help="Input file (image or PDF)")
    p.add_argument("--language", default="eng", help="Language code (default: eng)")
    p.add_argument("--profile", choices=["fast", "balanced", "quality"], default="balanced",
                   help="Preprocessing profile (default: balanced)")
    p.add_argument("--mode", choices=["auto", "force"], default="auto",
                   help="OCR mode for PDFs (default: auto)")
    p.add_argument("--format", choices=["txt", "json", "html"], default="txt",
                   help="Output format (default: txt)")
    p.add_argument("--output", help="Output file path")
    
    # ocr-status
    sub.add_parser("ocr-status", help="Check OCR engine availability")
    
    # pdf-extract-images
    p = sub.add_parser("pdf-extract-images", help="Extract pages as images")
    p.add_argument("input", help="Input PDF")
    p.add_argument("--output", help="Output prefix")
    
    args = parser.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    if args.command == "convert":
        _handle_convert(args)
    elif args.command == "images-to-pdf":
        _handle_images_to_pdf(args)
    elif args.command == "pdf-merge":
        _handle_pdf_merge(args)
    elif args.command == "pdf-split":
        _handle_pdf_split(args)
    elif args.command == "pdf-to-images":
        _handle_pdf_to_images(args)
    elif args.command == "pdf-text":
        _handle_pdf_text(args)
    elif args.command == "pdf-search":
        _handle_pdf_search(args)
    elif args.command == "pdf-info":
        _handle_pdf_info(args)
    elif args.command == "pdf-compress":
        _handle_pdf_compress(args)
    elif args.command == "pdf-watermark":
        _handle_pdf_watermark(args)
    elif args.command == "pdf-reorder":
        _handle_pdf_reorder(args)
    elif args.command == "pdf-delete":
        _handle_pdf_delete(args)
    elif args.command == "pdf-extract-images":
        _handle_pdf_extract_images(args)
    elif args.command == "formats":
        _handle_formats()
    elif args.command == "doctor":
        _handle_doctor()
    elif args.command == "office-status":
        _handle_office_status()
    elif args.command == "ocr":
        _handle_ocr(args)
    elif args.command == "ocr-status":
        _handle_ocr_status(args)
    else:
        parser.print_help()


def _handle_convert(args):
    from engine.converters.docx_to_pdf import docx_to_pdf
    from engine.converters.markdown_to_pdf import markdown_to_pdf
    from engine.converters.csv_xlsx import csv_to_xlsx, xlsx_to_csv
    from engine.converters.docx_odt import docx_to_odt, odt_to_docx
    from engine.converters.docx_convert import (docx_to_html, html_to_docx, docx_to_txt,
                                                txt_to_docx, docx_to_markdown,
                                                markdown_to_docx, docx_to_epub)
    from engine.converters.docx_to_pdf_v2 import odt_to_pdf, txt_to_pdf
    from engine.converters.pptx_convert import (pptx_to_pdf, pptx_to_images,
                                                pptx_to_docx, docx_to_pptx)
    from engine.converters.pdf_to_office import pdf_to_docx, pdf_to_pptx
    from engine.converters.spreadsheet_pdf import xlsx_to_pdf, ods_to_xlsx, xlsx_to_ods
    from engine.converters.docx_odt import odt_to_docx

    input_path = args.input
    fmt = args.to.lower()

    if input_path.endswith(".docx") and fmt == "pdf":
        from engine.converters.docx_to_pdf_v2 import docx_to_pdf as docx_to_pdf_v2
        r = docx_to_pdf_v2(input_path, args.output)
    elif input_path.endswith(".md") and fmt == "pdf":
        r = markdown_to_pdf(input_path, args.output)
    elif input_path.endswith(".txt") and fmt == "pdf":
        r = txt_to_pdf(input_path, args.output)
    elif input_path.endswith(".csv") and fmt == "xlsx":
        r = csv_to_xlsx(input_path, args.output)
    elif input_path.endswith(".xlsx") and fmt == "csv":
        r = xlsx_to_csv(input_path, args.output)
    elif input_path.endswith(".xlsx") and fmt == "pdf":
        r = xlsx_to_pdf(input_path, args.output)
    elif input_path.endswith(".xlsx") and fmt == "ods":
        r = xlsx_to_ods(input_path, args.output)
    elif input_path.endswith(".ods") and fmt == "xlsx":
        r = ods_to_xlsx(input_path, args.output)
    elif input_path.endswith(".docx") and fmt == "odt":
        r = docx_to_odt(input_path, args.output)
    elif input_path.endswith(".odt") and fmt == "docx":
        r = odt_to_docx(input_path, args.output)
    elif input_path.endswith(".odt") and fmt == "pdf":
        r = odt_to_pdf(input_path, args.output)
    elif input_path.endswith(".pdf") and fmt == "odt":
        from engine.converters.docx_to_pdf_v2 import pdf_to_odt
        r = pdf_to_odt(input_path, args.output)
    elif input_path.endswith(".pdf") and fmt == "docx":
        r = pdf_to_docx(input_path, args.output)
    elif input_path.endswith(".pdf") and fmt == "pptx":
        r = pdf_to_pptx(input_path, args.output)
    elif input_path.endswith(".docx") and fmt == "html":
        r = docx_to_html(input_path, args.output)
    elif input_path.endswith(".html") and fmt == "docx":
        r = html_to_docx(input_path, args.output)
    elif input_path.endswith(".docx") and fmt == "txt":
        r = docx_to_txt(input_path, args.output)
    elif input_path.endswith(".txt") and fmt == "docx":
        r = txt_to_docx(input_path, args.output)
    elif input_path.endswith(".docx") and fmt == "md":
        r = docx_to_markdown(input_path, args.output)
    elif input_path.endswith(".md") and fmt == "docx":
        r = markdown_to_docx(input_path, args.output)
    elif input_path.endswith(".docx") and fmt == "pptx":
        r = docx_to_pptx(input_path, args.output)
    elif input_path.endswith(".docx") and fmt == "epub":
        r = docx_to_epub(input_path, args.output)
    elif input_path.endswith(".pptx") and fmt == "pdf":
        r = pptx_to_pdf(input_path, args.output)
    elif input_path.endswith(".pptx") and fmt in ("png", "jpg", "jpeg", "images"):
        r = pptx_to_images(input_path, args.output)
    elif input_path.endswith(".pptx") and fmt == "docx":
        r = pptx_to_docx(input_path, args.output)
    else:
        print(f"Conversion {args.input} -> {fmt}: Not supported locally")
        return

    if r["success"]:
        fid = r.get("fidelity", "")
        print(f"Success: {r['output']} ({r.get('size','?')} bytes) [{r.get('method','?')}] {f'[{fid}]' if fid else ''}")
    else:
        print(f"Failed: {r['error']}")


def _handle_images_to_pdf(args):
    from engine.converters.images_to_pdf import images_to_pdf
    r = images_to_pdf(args.images, output_path=args.output, page_size=args.page_size,
                       orientation=args.orientation, quality=args.quality)
    if r["success"]:
        print(f"Images->PDF: {r['output']} ({r['size']} bytes, {r['pages']} pages)")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_merge(args):
    from engine.converters.pdf_merge import pdf_merge
    r = pdf_merge(args.pdfs, output_path=args.output)
    if r["success"]:
        print(f"PDFs merged: {r['output']} ({r['size']} bytes)")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_split(args):
    from engine.converters.pdf_split import pdf_split
    r = pdf_split(args.input, args.pages, output_path=args.output)
    if r["success"]:
        print(f"PDF split: {r['output']} ({r['size']} bytes)")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_to_images(args):
    from engine.converters.pdf_to_images import pdf_to_images
    r = pdf_to_images(args.input, output_path=args.output, format=args.format, dpi=args.dpi)
    if r["success"]:
        print(f"PDF->images: {r['count']} files generated")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_text(args):
    from engine.converters.pdf_text import extract_text
    r = extract_text(args.input, args.output)
    if r["success"]:
        print(f"Text extracted: {r['pages']} pages, {len(r['text'])} chars")
        if args.output:
            print(f"Output: {args.output}")
        else:
            print(r['text'][:500])
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_search(args):
    from engine.converters.pdf_text import search_text
    r = search_text(args.input, args.query, args.case_sensitive)
    if r["success"]:
        print(f"Found {r['total_matches']} matches for '{args.query}':")
        for m in r['matches'][:20]:
            print(f"  Page {m['page']} at position {m['position']}")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_info(args):
    from engine.converters.pdf_text import get_page_info
    r = get_page_info(args.input)
    if r["success"]:
        for key, val in r.items():
            if key != "success":
                print(f"  {key}: {val}")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_compress(args):
    from engine.converters.pdf_compress import compress_pdf
    r = compress_pdf(args.input, args.output, args.dpi)
    if r["success"]:
        print(f"PDF compressed: {r['output']} ({r['method']})")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_watermark(args):
    from engine.converters.pdf_text import add_text_watermark, extract_text
    r = add_text_watermark(args.input, args.text, args.output)
    if r["success"]:
        print(f"Watermark added: {r['output']} (text='{r['watermark']}')")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_reorder(args):
    from engine.converters.pdf_reorder import reorder_pages
    pages = [int(x.strip()) for x in args.pages.split(',')]
    r = reorder_pages(args.input, pages, args.output)
    if r["success"]:
        print(f"Pages reordered: {r['output']} (order={r['order']})")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_delete(args):
    from engine.converters.pdf_reorder import delete_pages
    pages = [int(x.strip()) for x in args.pages.split(',')]
    r = delete_pages(args.input, pages, args.output)
    if r["success"]:
        print(f"Pages deleted: {r['output']}")
    else:
        print(f"Failed: {r['error']}")


def _handle_pdf_extract_images(args):
    from engine.converters.pdf_text import extract_images
    r = extract_images(args.input, args.output)
    if r["success"]:
        print(f"Extracted {r['count']} images: {', '.join(r['images'])}")
    else:
        print(f"Failed: {r['error']}")


def _handle_formats():
    from engine.registry import get_registry
    r = get_registry()
    print("Supported formats:", ", ".join(r.get_supported_formats()))
    print()
    for name, info in r.engines.items():
        if info.get("installed"):
            v = info.get("version", "?")
            caps = info.get("capabilities", [])
            print(f"  OK {name} ({v}): {', '.join(caps) if caps else 'general'}")


def _handle_doctor():
    from engine.registry import get_registry
    r = get_registry()
    report = r.health_report()
    print(f"IconForge v{report['version']}")
    print(f"Healthy engines: {report['healthy']}/{report['total']}")
    print()
    for name, info in report['engines'].items():
        status = "OK" if info.get("installed") else "MISSING"
        v = info.get("version", "?")
        print(f"  {status} {name}: {v}")
    
    from engine.config import OUTPUT_DIR, TEMP_DIR, PRIVACY_MESSAGE
    print()
    print(f"Output: {OUTPUT_DIR}")
    print(f"Temp: {TEMP_DIR}")
    print(f"Privacy: {PRIVACY_MESSAGE}")


def _handle_office_status():
    from engine.registry import get_registry
    r = get_registry()
    status = r.office_status()
    print(f"ICON DocForge v{status['version']} — Office Conversion Status")
    print(f"Fonts installed: {status['fonts_installed']} (DejaVu: {status['dejavu_available']})")
    print()
    print(f"{'CONVERSION':22s} {'SUPPORTED':10s} {'FIDELITY':24s} METHOD")
    print("-" * 92)
    for c in status["conversions"]:
        mark = "yes" if c["supported"] else "no"
        print(f"{c['path']:22s} {mark:10s} {c['fidelity']:24s} {c['method']}")
    if status["unsupported"]:
        print()
        print("Unsupported locally:", ", ".join(status["unsupported"]))
        print("(no LibreOffice / ODP renderer on Termux; see OFFICE_LIMITATIONS.md)")


def _handle_ocr(args):
    """Handle OCR command."""
    from engine.converters.ocr_pipeline import run_ocr
    
    output_format = getattr(args, 'format', 'txt') or 'txt'
    language = getattr(args, 'language', 'eng') or 'eng'
    profile = getattr(args, 'profile', 'balanced') or 'balanced'
    mode = getattr(args, 'mode', 'auto') or 'auto'
    
    result = run_ocr(
        input_path=args.input,
        language=language,
        profile=profile,
        mode=mode,
        output_format=output_format,
    )
    
    if result["success"]:
        # Write to file if specified
        if hasattr(args, 'output') and args.output:
            os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result["text"])
            print(f"OCR complete: {args.output}")
        else:
            print(result["text"])
        
        print(f"\nConfidence: {result.get('confidence', 0):.1%}")
        print(f"Engine: {result.get('engine', 'unknown')}")
    else:
        print(f"OCR failed: {', '.join(result.get('errors', ['Unknown error']))}")


def _handle_ocr_status(args):
    """Handle ocr-status command."""
    from engine.ocr_engine import get_ocr_manager
    mgr = get_ocr_manager()
    status = mgr.ocr_status()
    
    print(f"OCR Status: {status['status'].upper()}")
    print(f"Primary engine: {status['primary_engine']}")
    print()
    print("Available engines:")
    for name, info in status['engines'].items():
        avail = "✓" if info['available'] else "✗"
        print(f"  [{avail}] {name}: v{info['version']}")
    if status['recommendations']:
        print()
        print("Recommendations:")
        for rec in status['recommendations']:
            print(f"  • {rec}")


if __name__ == "__main__":
    main()
