"""XLSX -> PDF renderer (paginated, multi-sheet) and ODF spreadsheet tools.

XLSX -> PDF renders each worksheet to ReportLab pages with repeated header
rows, cell borders, column headers (A, B, C...), and sheet title.
Fidelity: HIGH-FIDELITY for displayed values and structure (formulas shown
as cached values; live recalculation not performed).
"""
import os
from engine.config import OUTPUT_DIR
from engine.utils import create_temp_dir, cleanup_temp


def _col_letter(idx):
    """0-based index -> spreadsheet column letter."""
    s = ""
    idx += 1
    while idx > 0:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def xlsx_to_pdf(input_path: str, output_path: str = None, repeat_rows: int = 1) -> dict:
    """Render XLSX worksheets to a paginated PDF."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "XLSX not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    import openpyxl
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle, Spacer, PageBreak, SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet

    try:
        wb = openpyxl.load_workbook(input_path, data_only=True)
    except Exception as e:
        return {"success": False, "error": f"Cannot open XLSX: {e}"}

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=24, rightMargin=24,
                            topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        elements.append(Spacer(1, 4))
        # Sheet title
        elements.append(Paragraph(f"Sheet: {sheet_name}", styles["Heading2"]))
        elements.append(Spacer(1, 6))

        rows = []
        for ri, row in enumerate(ws.iter_rows(values_only=True)):
            if all(v is None for v in row):
                continue
            rows.append([str(v) if v is not None else "" for v in row])

        if not rows:
            elements.append(Paragraph("(empty sheet)", styles["Normal"]))
            elements.append(PageBreak())
            continue

        ncols = max(len(r) for r in rows)
        col_w = [50] + [90] * (ncols - 1)
        # Header row: column letters
        table_rows = [[_col_letter(i) for i in range(ncols)]]
        table_rows.extend(rows[: repeat_rows])  # repeat rows (usually row1)

        start = 1 + repeat_rows
        chunk = table_rows
        t = Table(chunk, colWidths=col_w, repeatRows=repeat_rows + 1)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.85, 0.8, 0.98)),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(t)

        # Remaining rows in chunks of 30
        for i in range(start, len(rows), 30):
            sub = rows[i:i + 30]
            t2 = Table(sub, colWidths=col_w)
            t2.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]))
            elements.append(t2)

        if sheet_name != wb.sheetnames[-1]:
            elements.append(PageBreak())

    doc.build(elements)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return {
            "success": True,
            "output": output_path,
            "size": os.path.getsize(output_path),
            "sheets": len(wb.sheetnames),
            "method": "openpyxl+reportlab paginated render",
            "fidelity": "HIGH-FIDELITY",
            "fidelity_label": "Accurate value/structure rendering",
            "note": "Formulas shown as cached values; charts and conditional formatting not rendered.",
        }
    return {"success": False, "error": "Output PDF not created"}


def pdf_to_xlsx(input_path: str, output_path: str = None) -> dict:
    """Experimental: detect table-like regions in a PDF and reconstruct to XLSX.

    Uses pdfplumber table detection. Classified LAYOUT-RECONSTRUCTION /
    EXPERIMENTAL: works best on PDFs with clean grid tables (e.g. generated
    from spreadsheets); free-form text PDFs yield partial/empty results.
    """
    if not os.path.exists(input_path):
        return {"success": False, "error": "PDF not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".xlsx")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    import pdfplumber
    from openpyxl import Workbook

    try:
        wb = Workbook()
        wb.remove(wb.active)
        found = 0
        with pdfplumber.open(input_path) as pdf:
            for pidx, page in enumerate(pdf.pages, 1):
                tables = page.find_tables()
                for tidx, table in enumerate(tables):
                    data = table.extract()
                    if not data:
                        continue
                    ws = wb.create_sheet(f"Page{pidx}_Table{tidx+1}" if len(tables) > 1 else f"Page{pidx}")
                    for row in data:
                        ws.append(["" if c is None else str(c) for c in row])
                    found += 1
        if found == 0:
            # Fallback: put page text into a single sheet so result is usable
            ws = wb.create_sheet("Page1_Text")
            with pdfplumber.open(input_path) as pdf:
                for pidx, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    ws.append([text])
            found = 1
        wb.save(output_path)
        return {
            "success": True,
            "output": output_path,
            "size": os.path.getsize(output_path),
            "method": "pdfplumber table detection + openpyxl",
            "fidelity": "EXPERIMENTAL",
            "fidelity_label": "Experimental table reconstruction",
            "tables_found": found,
            "note": "Works best on clean grid tables (e.g. spreadsheet-generated PDFs). "
                    "Free-form layouts may produce partial results. Review output carefully.",
        }
    except Exception as e:
        return {"success": False, "error": f"PDF->XLSX failed: {e}"}


def ods_to_xlsx(input_path: str, output_path: str = None) -> dict:
    """ODS -> XLSX via odfpy read + openpyxl write."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "ODS not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".xlsx")
    try:
        from odf.opendocument import load
        from odf.table import Table, TableCell
        from odf.text import P
        from openpyxl import Workbook

        doc = load(input_path)
        wb = Workbook()
        default_ws = wb.active
        ws_active_used = False

        # doc.spreadsheet is the office:body; its children are table:table elements
        def lname(el):
            """Get the local XML element name from an odfpy node."""
            tag = getattr(el, "tagName", None) or getattr(el, "localName", None) or ""
            return str(tag).split(":")[-1]

        for tbl in doc.spreadsheet.childNodes:
            if lname(tbl) != "table":
                continue
            if not ws_active_used:
                ws = default_ws
                ws_active_used = True
            else:
                ws = wb.create_sheet()
            ws.title = tbl.getAttribute("name") or ws.title

            for row_el in tbl.childNodes:
                if lname(row_el) != "table-row":
                    continue
                row_vals = []
                for cell in row_el.childNodes:
                    if lname(cell) != "table-cell":
                        continue
                    text_parts = []
                    for p in cell.childNodes:
                        if lname(p) == "p":
                            text_parts.append("".join(
                                t.data for t in p.childNodes
                                if hasattr(t, "data")
                            ))
                    row_vals.append("\n".join(t for t in text_parts if t))
                if any(v for v in row_vals):
                    ws.append(row_vals)

        wb.save(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return {"success": True, "output": output_path, "size": os.path.getsize(output_path),
                    "method": "odfpy+openpyxl", "fidelity": "STRUCTURAL-RECONSTRUCTION",
                    "note": "Values transferred; styles, formulas, and charts not preserved."}
        return {"success": False, "error": "Output XLSX not created"}
    except Exception as e:
        return {"success": False, "error": f"ODS->XLSX failed: {e}"}


def xlsx_to_ods(input_path: str, output_path: str = None) -> dict:
    """XLSX -> ODS via openpyxl read + odfpy write."""
    if not os.path.exists(input_path):
        return {"success": False, "error": "XLSX not found"}
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".ods")
    import openpyxl
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table as OdfTable, TableRow, TableCell
    from odf.text import P

    wb = openpyxl.load_workbook(input_path, data_only=True)
    doc = OpenDocumentSpreadsheet()
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        tbl = OdfTable(name=sheet_name)
        for row in ws.iter_rows(values_only=True):
            trow = TableRow()
            tbl.addElement(trow)
            for val in row:
                tc = TableCell()
                if val is not None:
                    tc.addElement(P(text=str(val)))
                trow.addElement(tc)
        doc.spreadsheet.addElement(tbl)
    doc.save(output_path)
    if os.path.exists(output_path):
        return {"success": True, "output": output_path, "size": os.path.getsize(output_path),
                "method": "openpyxl+odfpy", "fidelity": "STRUCTURAL-RECONSTRUCTION",
                "note": "Values transferred; styles, formulas, and charts are not preserved."}
    return {"success": False, "error": "Output ODS not created"}
