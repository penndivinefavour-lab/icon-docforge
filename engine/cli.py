"""CLI interface for ICON DocForge."""
import sys
import os
import argparse
import json

def main():
    parser = argparse.ArgumentParser(
        prog="iconconvert",
        description="ICON DocForge - Offline-first document conversion CLI"
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
    
    # formats
    sub.add_parser("formats", help="List supported formats")
    
    # doctor
    sub.add_parser("doctor", help="Check engine health")
    
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
    elif args.command == "formats":
        _handle_formats()
    elif args.command == "doctor":
        _handle_doctor()
    else:
        parser.print_help()


def _handle_convert(args):
    from engine.converters.docx_to_pdf import docx_to_pdf
    from engine.converters.markdown_to_pdf import markdown_to_pdf
    from engine.converters.csv_xlsx import csv_to_xlsx, xlsx_to_csv
    from engine.converters.docx_odt import docx_to_odt, odt_to_docx
    
    input_path = args.input
    fmt = args.to.lower()
    
    if input_path.endswith(".docx") and fmt == "pdf":
        r = docx_to_pdf(input_path, args.output)
    elif input_path.endswith(".md") and fmt == "pdf":
        r = markdown_to_pdf(input_path, args.output)
    elif input_path.endswith(".csv") and fmt == "xlsx":
        r = csv_to_xlsx(input_path, args.output)
    elif input_path.endswith(".xlsx") and fmt == "csv":
        r = xlsx_to_csv(input_path, args.output)
    elif input_path.endswith(".docx") and fmt == "odt":
        r = docx_to_odt(input_path, args.output)
    elif input_path.endswith(".odt") and fmt == "docx":
        r = odt_to_docx(input_path, args.output)
    else:
        print(f"Conversion {args.input} → {fmt}: Not supported locally")
        return
    
    if r["success"]:
        print(f"✅ Success: {r['output']} ({r.get('size', '?')} bytes) [{r.get('method', '?')}]")
    else:
        print(f"❌ Failed: {r['error']}")


def _handle_images_to_pdf(args):
    from engine.converters.images_to_pdf import images_to_pdf
    r = images_to_pdf(args.images, output_path=args.output, page_size=args.page_size,
                       orientation=args.orientation, quality=args.quality)
    if r["success"]:
        print(f"✅ Images→PDF: {r['output']} ({r['size']} bytes, {r['pages']} pages)")
    else:
        print(f"❌ Failed: {r['error']}")


def _handle_pdf_merge(args):
    from engine.converters.pdf_merge import pdf_merge
    r = pdf_merge(args.pdfs, output_path=args.output)
    if r["success"]:
        print(f"✅ PDFs merged: {r['output']} ({r['size']} bytes)")
    else:
        print(f"❌ Failed: {r['error']}")


def _handle_pdf_split(args):
    from engine.converters.pdf_split import pdf_split
    r = pdf_split(args.input, args.pages, output_path=args.output)
    if r["success"]:
        print(f"✅ PDF split: {r['output']} ({r['size']} bytes)")
    else:
        print(f"❌ Failed: {r['error']}")


def _handle_pdf_to_images(args):
    from engine.converters.pdf_to_images import pdf_to_images
    r = pdf_to_images(args.input, output_path=args.output, format=args.format, dpi=args.dpi)
    if r["success"]:
        print(f"✅ PDF→images: {r['count']} files generated")
    else:
        print(f"❌ Failed: {r['error']}")


def _handle_formats():
    from engine.registry import get_registry
    r = get_registry()
    print("Supported formats:", ", ".join(r.get_supported_formats()))
    print()
    for name, info in r.engines.items():
        if info.get("installed"):
            v = info.get("version", "?")
            caps = info.get("capabilities", [])
            print(f"  ✅ {name} ({v}): {', '.join(caps) if caps else 'general'}")


def _handle_doctor():
    from engine.registry import get_registry
    r = get_registry()
    report = r.health_report()
    print(f"🔧 {report['product']} v{report['version']}")
    print(f"   Healthy engines: {report['healthy']}/{report['total']}")
    print()
    for name, info in report['engines'].items():
        status = "✅" if info.get("installed") else "❌"
        v = info.get("version", "?")
        print(f"  {status} {name}: {v}")
    
    import os
    print()
    print(f"📁 Output dir: {os.path.expanduser(str(r.engines.get('pandoc', {})))}")
    from engine.config import OUTPUT_DIR, TEMP_DIR
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"📁 Temp: {TEMP_DIR}")
    print(f"💾 Privacy: {__import__('engine.config', fromlist=['PRIVACY_MESSAGE']).PRIVACY_MESSAGE}")


if __name__ == "__main__":
    main()
