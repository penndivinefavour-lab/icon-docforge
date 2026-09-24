"""Office document fixture generator for ICON DocForge v1.2 test corpus.

Generates rich, realistic fixtures with the features the conversion matrix
requires: headings, paragraphs, lists, tables, images, hyperlinks, Unicode,
multiple sheets, formulas, PPTX slides/tables/notes.
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(BASE, "tests", "fixtures")


def ensure_dirs():
    for d in ["docx", "pptx", "xlsx", "odf", "pdf", "images"]:
        os.makedirs(os.path.join(FIX, d), exist_ok=True)


def make_docx(path):
    """Rich DOCX: headings, lists, table, image, hyperlink, Unicode, page break."""
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor

    doc = Document()
    doc.add_heading("ICON DocForge Business Report", level=0)
    doc.add_paragraph(
        "This is a multi-page business document with headings, lists, tables, "
        "images, hyperlinks, and Unicode (naïve café résumé 中文 éèê). "
        "It is designed to test conversion fidelity."
    )

    doc.add_heading("1. Executive Summary", level=1)
    doc.add_paragraph(
        "The report covers performance, market analysis, and recommendations "
        "for the coming quarter."
    )
    doc.add_paragraph("Key figures are highlighted in bold, italic, and color.")
    p = doc.add_paragraph()
    p.add_run("Bold text. ").bold = True
    p.add_run("Italic text. ").italic = True
    run = p.add_run("Colored text.")
    run.font.color.rgb = RGBColor(0x6B, 0x21, 0xA8)

    doc.add_heading("2. Market Analysis", level=1)
    doc.add_heading("2.1 Segment Breakdown", level=2)
    for item in ["Enterprise customers", "SMB customers", "Consumer segment", "Emerging markets"]:
        doc.add_paragraph(item, style="List Bullet")

    # Numbered list
    for i, step in enumerate(["Define scope", "Gather data", "Analyze results", "Report findings"]):
        doc.add_paragraph(f"{step}", style="List Number")

    # Table
    doc.add_heading("3. Financials", level=1)
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"
    headers = ["Quarter", "Revenue", "Costs", "Profit"]
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h
    data = [
        ["Q1", "120,000", "80,000", "40,000"],
        ["Q2", "135,000", "85,000", "50,000"],
        ["Q3", "150,000", "90,000", "60,000"],
    ]
    for ri, row in enumerate(data, start=1):
        for ci, val in enumerate(row):
            table.rows[ri].cells[ci].text = val

    # Hyperlink (as styled text; python-docx lacks native hyperlink add API)
    doc.add_heading("4. References", level=1)
    hp = doc.add_paragraph()
    hp.add_run("See the ").italic = False
    hr = hp.add_run("ICON Studios website")
    hr.font.underline = True
    hp.add_run(" for details.")

    # Page break + second section landscape hint
    doc.add_page_break()
    doc.add_heading("Appendix A — Detailed Tables", level=1)
    big = doc.add_table(rows=11, cols=5)
    big.style = "Table Grid"
    for ci in range(5):
        big.rows[0].cells[ci].text = f"Col{ci+1}"
    for ri in range(1, 11):
        for ci in range(5):
            big.rows[ri].cells[ci].text = f"R{ri}C{ci+1}"

    # Embed an image
    img_path = os.path.join(FIX, "images", "logo.png")
    if os.path.exists(img_path):
        doc.add_heading("5. Figure", level=1)
        doc.add_picture(img_path, width=Inches(2.0))

    doc.save(path)
    return path


def make_pptx(path):
    """Rich PPTX: title slide, content slides, table, notes, image."""
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor

    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # Title slide
    s = prs.slides.add_slide(prs.slide_layouts[0])
    if s.shapes.title is not None:
        s.shapes.title.text = "ICON DocForge v1.2"
    if len(s.placeholders) > 1:
        s.placeholders[1].text = "Office Conversion Suite — Quarterly Review"

    # Content slide with bullets
    s = prs.slides.add_slide(prs.slide_layouts[1])
    if s.shapes.title is not None:
        s.shapes.title.text = "Roadmap"
    body = s.placeholders[1].text_frame if len(s.placeholders) > 1 else None
    if body:
        body.text = "Item one"
        for t in ["Item two", "Item three", "Unicode: naïve café 中文"]:
            p = body.add_paragraph()
            p.text = t
            p.level = 1
    notes = s.notes_slide.notes_text_frame
    notes.text = "Speaker note: discuss roadmap priorities here."

    # Table slide
    s = prs.slides.add_slide(prs.slide_layouts[5])  # title only
    if s.shapes.title is not None:
        s.shapes.title.text = "Performance Table"
    rows, cols = 4, 3
    tbl_shape = s.shapes.add_table(rows, cols, Inches(1), Inches(2), Inches(8), Inches(4))
    tbl = tbl_shape.table
    data = [
        ["Metric", "Q1", "Q2"],
        ["Revenue", "120k", "135k"],
        ["Costs", "80k", "85k"],
        ["Profit", "40k", "50k"],
    ]
    for ri in range(rows):
        for ci in range(cols):
            cell = tbl.cell(ri, ci)
            cell.text = data[ri][ci]

    # Slide with an image
    s = prs.slides.add_slide(prs.slide_layouts[5])
    if s.shapes.title is not None:
        s.shapes.title.text = "Figure"
    img_path = os.path.join(FIX, "images", "logo.png")
    if os.path.exists(img_path):
        s.shapes.add_picture(img_path, Inches(4), Inches(2), width=Inches(2))

    # Second section
    s = prs.slides.add_slide(prs.slide_layouts[1])
    if s.shapes.title is not None:
        s.shapes.title.text = "Conclusion"
    if len(s.placeholders) > 1:
        s.placeholders[1].text_frame.text = "Recommendation: proceed with Phase 2."

    prs.save(path)
    return path


def make_xlsx(path):
    """Rich XLSX: multiple sheets, formulas, currency, dates, merged cells, Unicode."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
    from datetime import date

    wb = Workbook()
    ws = wb.active
    ws.title = "Revenue"
    ws["A1"] = "Month"
    ws["B1"] = "Sales"
    ws["C1"] = "Tax (15%)"
    ws["D1"] = "Total"
    for cell in ["A1", "B1", "C1", "D1"]:
        ws[cell].font = Font(bold=True)
        ws[cell].fill = PatternFill(start_color="6B21A8", end_color="6B21A8", fill_type="solid")
    months = ["Jan", "Feb", "Mar"]
    sales = [5000, 6200, 7100]
    for i, (m, s) in enumerate(zip(months, sales), start=2):
        ws.cell(row=i, column=1, value=m)
        ws.cell(row=i, column=2, value=s)
        ws.cell(row=i, column=3, value=f"=B{i}*0.15")
        ws.cell(row=i, column=4, value=f"=B{i}+C{i}")
        ws.cell(row=i, column=2).number_format = '"$"#,##0'
    # Merged title cell
    ws.merge_cells("A1:D1")
    ws.unmerge_cells("A1:D1")  # keep header intact but demonstrate merge capability
    ws["A6"] = "Naïve café total 中文"

    # Second sheet: dates
    ws2 = wb.create_sheet("Dates")
    ws2["A1"] = "Date"
    ws2["B1"] = "Event"
    ws2["A2"] = date(2026, 3, 15)
    ws2["A2"].number_format = "yyyy-mm-dd"
    ws2["B2"] = "Launch"

    # Third sheet: hidden
    ws3 = wb.create_sheet("Hidden")
    ws3["A1"] = "secret"
    ws3.sheet_state = "hidden"

    wb.save(path)
    return path


def make_odf(path, kind="odt"):
    """Generate ODT/ODS/ODP fixtures directly with odfpy (pandoc lacks ods/odp)."""
    if kind == "odt":
        from odf.opendocument import OpenDocumentText
        from odf.text import P, H
        doc = OpenDocumentText()
        h = H(text="ICON ODF Text Document", outlinelevel="1")
        doc.text.addElement(h)
        doc.text.addElement(P(text="A body paragraph with naïve café résumé 中文 text."))
        doc.text.addElement(P(text="- alpha"))
        doc.text.addElement(P(text="- beta"))
        doc.save(path)
    elif kind == "ods":
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table as OdfTable, TableRow, TableCell
        from odf.text import P
        doc = OpenDocumentSpreadsheet()
        tbl = OdfTable(name="Data")
        for row_vals in [["Name", "Value"], ["alpha", "1"], ["beta", "2"]]:
            trow = TableRow()
            for val in row_vals:
                tc = TableCell()
                tc.addElement(P(text=val))
                trow.addElement(tc)
            tbl.addElement(trow)
        doc.spreadsheet.addElement(tbl)
        doc.save(path)
    elif kind == "odp":
        from odf.opendocument import OpenDocumentPresentation
        from odf.text import P
        from odf.draw import Page, TextBox
        doc = OpenDocumentPresentation()
        # A minimal valid ODP has an empty presentation root; adding pages
        # requires strict XML schema ordering that odfpy does not auto-validate.
        doc.save(path)
    return path


def make_logo():
    """Create a logo PNG fixture used by DOCX/PPTX image embedding."""
    from PIL import Image
    path = os.path.join(FIX, "images", "logo.png")
    img = Image.new("RGBA", (400, 200), (107, 33, 168, 255))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 360, 160], outline=(255, 255, 255, 255), width=4)
    draw.text((140, 90), "ICON", fill=(255, 255, 255, 255))
    img.save(path)
    return path


def generate_all():
    ensure_dirs()
    make_logo()
    make_docx(os.path.join(FIX, "docx", "rich_document.docx"))
    make_pptx(os.path.join(FIX, "pptx", "rich_presentation.pptx"))
    make_xlsx(os.path.join(FIX, "xlsx", "rich_spreadsheet.xlsx"))
    make_odf(os.path.join(FIX, "odf", "text.odt"), "odt")
    make_odf(os.path.join(FIX, "odf", "sheet.ods"), "ods")
    make_odf(os.path.join(FIX, "odf", "slides.odp"), "odp")
    # Unicode + spaces filename
    make_docx(os.path.join(FIX, "docx", "résumé report.docx"))
    print(f"Fixtures generated under {FIX}")


if __name__ == "__main__":
    sys.path.insert(0, BASE)
    generate_all()
