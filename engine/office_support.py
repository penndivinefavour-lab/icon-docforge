"""Office-support utilities: font discovery, source preflight, output validation.

- discover_fonts(): finds locally installed TTF/OTF fonts so converters can
  choose sensible fallbacks instead of silently substituting.
- preflight(): inspects the source Office file and warns about features that
  may not survive conversion (macros, embedded objects, charts, encryption).
  It never executes macros or embedded content.
- validate_docx / validate_pptx / validate_xlsx / validate_pdf: parse the
  generated output with the appropriate library to confirm structural validity
  before it is handed to the user.
"""
import os
import glob
import re

# ---------------------------------------------------------------------------
# Font discovery
# ---------------------------------------------------------------------------

_FONT_CACHE = None

_FONT_DIRS = [
    "/data/data/com.termux/files/usr/share/fonts",
    "/system/fonts",
    "/usr/share/fonts",
    os.path.expanduser("~/.fonts"),
]


def discover_fonts(reset: bool = False):
    """Return a dict of available font families and system font paths.

    Caches results. Family keys map to a sorted list of available weights.
    """
    global _FONT_CACHE
    if _FONT_CACHE is not None and not reset:
        return _FONT_CACHE

    families = {}
    all_paths = []
    for d in _FONT_DIRS:
        for ext in ("*.ttf", "*.otf", "*.ttc"):
            all_paths.extend(glob.glob(os.path.join(d, "**", ext), recursive=True))
    all_paths = sorted(set(all_paths))

    for p in all_paths:
        base = os.path.splitext(os.path.basename(p))[0]
        # Strip weight/style suffixes to get a family-ish key
        key = base
        for suffix in ("-BoldItalic", "-Italic", "-Oblique", "-Bold", "-Light", "-Condensed", "-Mono"):
            key = key.replace(suffix, "")
        families.setdefault(key, []).append(base)

    _FONT_CACHE = {
        "families": families,
        "paths": all_paths,
        "count": len(all_paths),
        "has_dejavu": any("DejaVu" in os.path.basename(p) for p in all_paths),
    }
    return _FONT_CACHE


def pick_fallback(requested_family: str):
    """Pick a locally available family for a requested (possibly missing) font.

    Returns (chosen_family, is_fallback: bool).
    """
    fonts = discover_fonts()
    avail = set(fonts["families"].keys())
    if requested_family and requested_family in avail:
        return requested_family, False
    # Prefer DejaVu (full Unicode) over others
    for pref in ["DejaVuSerif", "DejaVuSans", "DejaVuSans Mono", "LiberationSerif", "LiberationSans"]:
        if pref in avail:
            return pref, True
    # Any available family
    if avail:
        return sorted(avail)[0], True
    return None, True


# ---------------------------------------------------------------------------
# Source preflight (never executes macros / embedded content)
# ---------------------------------------------------------------------------

def preflight(input_path: str):
    """Inspect an Office source file and report unsupported/dangerous features.

    Returns {"warnings": [..], "stripped": [..], "blocked": bool}.
    Macros and OLE objects are flagged (never executed); they are stripped
    for safety on conversion.
    """
    warnings = []
    stripped = []
    blocked = False
    ext = os.path.splitext(input_path)[1].lower()

    if not os.path.exists(input_path):
        return {"warnings": ["File not found"], "blocked": True}

    size = os.path.getsize(input_path)
    if size == 0:
        return {"warnings": ["File is empty (0 bytes)"], "blocked": True}

    # Quick OLE2 / ZIP sniff for dangerous embedded content
    with open(input_path, "rb") as fh:
        head = fh.read(512)
    if head[:4] == b"\xd0\xcf\x11\xe0":
        # OLE2 compound (legacy .doc/.ppt) — may contain OLE objects
        warnings.append("Legacy OLE2 container; may contain embedded objects (stripped for safety)")
        stripped.append("embedded-ole-objects")
    elif head[:4] == b"PK\x03\x04":
        # ZIP (docx/xlsx/pptx/ods) — check for macro signatures
        pass

    if ext == ".doc":
        warnings.append("Legacy .doc (binary); recommend .docx for best fidelity")
    if ext in (".docx", ".pptx", ".xlsx"):
        import zipfile
        try:
            with zipfile.ZipFile(input_path) as zf:
                names = zf.namelist()
                joined = " ".join(names)
                if "vbaProject" in joined or any(n.endswith(".bin") and "vba" in n.lower() for n in names):
                    warnings.append("Contains VBA macros (NOT executed; ignored for safety)")
                    stripped.append("vba-macros")
                if "oleObject" in joined or "embeddings" in joined:
                    warnings.append("Contains embedded OLE objects (ignored for safety)")
                    stripped.append("embedded-ole-objects")
                if "charts" in joined or any("chart" in n for n in names):
                    warnings.append("Contains charts (not rendered in Office→PDF; shown as values only)")
                    stripped.append("charts")
        except Exception as e:
            warnings.append(f"Cannot inspect archive: {str(e)[:80]}")

    if ext == ".pdf":
        # Encrypted PDF?
        try:
            import PyPDF2
            r = PyPDF2.PdfReader(input_path)
            if r.is_encrypted:
                warnings.append("PDF is password-protected; decryption password required")
                blocked = True
        except Exception:
            pass

    return {"warnings": warnings, "stripped": stripped, "blocked": blocked}


# ---------------------------------------------------------------------------
# Post-conversion structural validation
# ---------------------------------------------------------------------------

def validate_docx(path: str) -> dict:
    from docx import Document
    try:
        d = Document(path)
        return {"valid": True, "paragraphs": len(d.paragraphs), "tables": len(d.tables),
                "sections": len(d.sections)}
    except Exception as e:
        return {"valid": False, "error": str(e)[:150]}


def validate_pptx(path: str) -> dict:
    from pptx import Presentation
    try:
        p = Presentation(path)
        slides = list(p.slides)
        shapes = [len(s.shapes) for s in slides]
        return {"valid": True, "slides": len(slides), "shape_counts": shapes}
    except Exception as e:
        return {"valid": False, "error": str(e)[:150]}


def validate_xlsx(path: str) -> dict:
    from openpyxl import load_workbook
    try:
        wb = load_workbook(path)
        sheets = []
        for n in wb.sheetnames:
            ws = wb[n]
            sheets.append({"name": n, "rows": ws.max_row, "cols": ws.max_column,
                           "state": ws.sheet_state})
        return {"valid": True, "sheets": sheets}
    except Exception as e:
        return {"valid": False, "error": str(e)[:150]}


def validate_pdf(path: str) -> dict:
    import PyPDF2
    try:
        r = PyPDF2.PdfReader(path)
        info = {}
        if r.metadata:
            for k in ("/Title", "/Author", "/Producer", "/Creator"):
                v = r.metadata.get(k)
                if v:
                    info[str(k)] = str(v)
        return {"valid": True, "pages": len(r.pages), "encrypted": r.is_encrypted,
                "metadata": info}
    except Exception as e:
        return {"valid": False, "error": str(e)[:150]}


def validate_any(path: str) -> dict:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return validate_docx(path)
    if ext == ".pptx":
        return validate_pptx(path)
    if ext in (".xlsx", ".ods"):
        return validate_xlsx(path)
    if ext == ".pdf":
        return validate_pdf(path)
    if ext == ".odt":
        from odf.opendocument import load
        try:
            load(path)
            return {"valid": True}
        except Exception as e:
            return {"valid": False, "error": str(e)[:150]}
    if ext == ".html":
        return {"valid": os.path.exists(path), "note": "basic existence check"}
    return {"valid": True, "note": "no structural validator for this format"}
