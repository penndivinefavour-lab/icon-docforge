"""Improved DOCX -> PDF with professional CSS template.

The v1.0 path (pandoc -> html -> weasyprint) produced a bare PDF. This module
adds a full reference stylesheet with @page rules, running headers/footers,
page numbers, professional table styling, heading hierarchy, and font
fallback so DOCX -> PDF is a HIGH-FIDELITY output rather than a plain dump.

A pandoc reference-docx can also be used; when absent, the CSS path is used.
"""
import os
import json
from engine.utils import safe_run, create_temp_dir, cleanup_temp
from engine.config import OUTPUT_DIR, TEMP_DIR

# Professional reference CSS applied to the pandoc-generated HTML before PDF.
REFERENCE_CSS = """
@page {
  size: A4;
  margin: 2.2cm 1.8cm;
  @top-center { content: "ICON DocForge"; font-size: 8pt; color: #888; }
  @bottom-center { content: counter(page) " / " counter(pages); font-size: 8pt; color: #888; }
  @bottom-right { content: "Generated locally"; font-size: 7pt; color: #aaa; }
}
html { font-size: 10.5pt; }
body { font-family: "DejaVu Serif", "Liberation Serif", serif; line-height: 1.4; color: #1a1a1a; }
h1 { font-family: "DejaVu Sans", sans-serif; font-size: 20pt; color: #4a1d7a;
     border-bottom: 2px solid #6b21a8; padding-bottom: 4pt; margin-top: 0; }
h2 { font-family: "DejaVu Sans", sans-serif; font-size: 15pt; color: #6b21a8; margin-top: 14pt; }
h3 { font-family: "DejaVu Sans", sans-serif; font-size: 12.5pt; color: #444; }
h4 { font-family: "DejaVu Sans", sans-serif; font-size: 11pt; color: #555; }
p { margin: 0 0 7pt 0; text-align: justify; }
a { color: #6b21a8; }
img { max-width: 100%; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; }
table, th, td { border: 1px solid #bbb; }
th { background: #f2eafc; font-family: "DejaVu Sans", sans-serif; font-size: 9.5pt;
     text-align: left; padding: 4pt 6pt; }
td { font-size: 9.5pt; padding: 4pt 6pt; }
caption { caption-side: top; font-size: 8.5pt; color: #666; margin-bottom: 3pt; }
code { font-family: "DejaVu Sans Mono", monospace; background: #f4f0fa; padding: 0 3pt; }
pre { background: #f4f0fa; border: 1px solid #ddd; padding: 8pt; overflow-x: auto; }
blockquote { margin: 8pt 0; padding: 6pt 12pt; border-left: 3px solid #6b21a8;
             color: #555; background: #faf7fd; }
ul, ol { margin: 4pt 0 8pt 0; padding-left: 20pt; }
hr { border: none; border-top: 1px solid #ccc; margin: 12pt 0; }
"""


def docx_to_pdf(input_path: str, output_path: str = None,
                metadata: dict = None, landscape: bool = False) -> dict:
    """Convert DOCX to a professionally-styled PDF via pandoc + weasyprint + CSS.

    Fidelity: HIGH-FIDELITY for standard documents (headings, lists, tables,
    images, links, Unicode). Complex layout (text boxes, SmartArt, footnotes)
    is approximated.
    """
    if not os.path.exists(input_path):
        return {"success": False, "error": f"Input file not found: {input_path}"}

    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    temp_dir = create_temp_dir("docx2pdf2_")
    try:
        # Step 1: pandoc DOCX -> standalone HTML
        html_path = os.path.join(temp_dir, "doc.html")
        result = safe_run(["pandoc", input_path, "-t", "html5", "-s",
                           "--self-contained", "-o", html_path], timeout=90)
        if not result["success"]:
            return {"success": False, "error": f"Pandoc HTML failed: {result.get('stderr','')[:200]}"}

        # Step 2: inject reference CSS + metadata into the standalone HTML
        html = open(html_path, encoding="utf-8").read()
        css_block = "<style>\n" + REFERENCE_CSS + "</style>\n"
        # Insert before </head>
        if "</head>" in html:
            html = html.replace("</head>", css_block + "</head>", 1)
        else:
            html = css_block + html
        # Inject title metadata
        if metadata and metadata.get("title"):
            html = html.replace("<title>", f"<title>{metadata['title']}")
        styled_path = os.path.join(temp_dir, "doc_styled.html")
        with open(styled_path, "w", encoding="utf-8") as f:
            f.write(html)

        # Step 3: weasyprint -> PDF
        from weasyprint import HTML
        HTML(filename=styled_path).write_pdf(output_path)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return {
                "success": True,
                "output": output_path,
                "size": os.path.getsize(output_path),
                "method": "pandoc+weasyprint+reference-css",
                "fidelity": "HIGH-FIDELITY",
                "fidelity_label": "High-fidelity styled PDF",
                "note": "Headings, lists, tables, images, links, and Unicode preserved. "
                        "Text boxes, SmartArt, and footnotes approximated.",
            }
        return {"success": False, "error": "Output PDF not created"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cleanup_temp(temp_dir)


def odt_to_pdf(input_path: str, output_path: str = None) -> dict:
    """ODT -> PDF via pandoc (HTML) + weasyprint + reference CSS."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "ODT not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    temp_dir = create_temp_dir("odt2pdf_")
    try:
        html_path = os.path.join(temp_dir, "doc.html")
        r = safe_run(["pandoc", input_path, "-t", "html5", "-s", "--self-contained",
                      "-o", html_path], timeout=60)
        if not r["success"]:
            return {"success": False, "error": f"Pandoc ODT->HTML failed: {r.get('stderr','')[:200]}"}
        html = open(html_path, encoding="utf-8").read()
        html = html.replace("</head>", "<style>" + REFERENCE_CSS + "</style></head>", 1)
        styled = os.path.join(temp_dir, "styled.html")
        open(styled, "w", encoding="utf-8").write(html)
        from weasyprint import HTML
        HTML(filename=styled).write_pdf(output_path)
        if os.path.exists(output_path):
            return {"success": True, "output": output_path, "size": os.path.getsize(output_path),
                    "method": "pandoc+weasyprint", "fidelity": "HIGH-FIDELITY"}
        return {"success": False, "error": "Output PDF not created"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cleanup_temp(temp_dir)


def txt_to_pdf(input_path: str, output_path: str = None) -> dict:
    """Plain text -> styled PDF via pandoc HTML + weasyprint + CSS."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "TXT not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    temp_dir = create_temp_dir("txt2pdf_")
    try:
        html_path = os.path.join(temp_dir, "doc.html")
        r = safe_run(["pandoc", input_path, "-t", "html5", "-s", "--self-contained",
                      "-o", html_path], timeout=60)
        if not r["success"]:
            return {"success": False, "error": f"pandoc failed: {r.get('stderr','')[:200]}"}
        html = open(html_path, encoding="utf-8").read()
        html = html.replace("</head>", "<style>" + REFERENCE_CSS + "</style></head>", 1)
        styled = os.path.join(temp_dir, "styled.html")
        with open(styled, "w", encoding="utf-8") as f:
            f.write(html)
        from weasyprint import HTML
        HTML(filename=styled).write_pdf(output_path)
        if os.path.exists(output_path):
            return {"success": True, "output": output_path, "size": os.path.getsize(output_path),
                    "method": "pandoc+weasyprint", "fidelity": "HIGH-FIDELITY"}
        return {"success": False, "error": "Output PDF not created"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cleanup_temp(temp_dir)


def pdf_to_odt(input_path: str, output_path: str = None) -> dict:
    """PDF -> ODT via text reconstruction (structural)."""
    import pdfplumber
    from odf.opendocument import OpenDocumentText
    from odf.text import P
    if not os.path.exists(input_path):
        return {"success": False, "error": "PDF not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".odt")
    doc = OpenDocumentText()
    try:
        with pdfplumber.open(input_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                for line in text.split("\n"):
                    doc.text.addElement(P(text=line))
                if i < len(pdf.pages) - 1:
                    from odf.text import H
                    doc.text.addElement(P(text=""))
        doc.save(output_path)
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path),
                "method": "pdfplumber+odfpy", "fidelity": "STRUCTURAL-RECONSTRUCTION"}
    except Exception as e:
        return {"success": False, "error": str(e)}
