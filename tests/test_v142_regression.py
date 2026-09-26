"""Regression tests for v1.4.2 Android frontend fixes.

Covers: tool-card interaction, bridge safety guards, client-side conversion paths.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
JS_TOOLS = WEB / "js" / "tools"
APP_JS = WEB / "js" / "app.js"


def test_pdf_reorder_has_onmount():
    """pdf-reorder.js must define onMount (was missing in v1.4.0)."""
    content = (JS_TOOLS / "pdf-reorder.js").read_text(encoding="utf-8")
    assert "async function onMount" in content or "function onMount" in content, \
        "pdf-reorder.js must implement onMount handler"


def test_androidbridge_guarded_in_docx_to_pdf():
    """docx-to-pdf.js must not call AndroidBridge methods without null guard."""
    content = (JS_TOOLS / "docx-to-pdf.js").read_text(encoding="utf-8")
    # Should use window.AndroidBridge && check, not bare AndroidBridge.
    # Allow either pattern.
    assert "window.AndroidBridge" in content or "AndroidBridge" in content
    # Verify there's a guard pattern
    has_guard = bool(re.search(r'window\.AndroidBridge\s*&&', content))
    assert has_guard, "docx-to-pdf.js must guard AndroidBridge calls"


def test_androidbridge_guarded_in_pdf_text_search():
    """pdf-text-search.js must not crash when AndroidBridge is absent."""
    content = (JS_TOOLS / "pdf-text-search.js").read_text(encoding="utf-8")
    assert "window.AndroidBridge" in content, "Must guard AndroidBridge access"


def test_csv_xlsx_uses_client_side_xlsx():
    """csv-xlsx.js must use XLSX library client-side, not localhost API."""
    content = (JS_TOOLS / "csv-xlsx.js").read_text(encoding="utf-8")
    # Must reference XLSX global (from xlsx.full.min.js vendor)
    assert "XLSX" in content, "Must use XLSX client-side library"
    # Must NOT try to fetch from localhost
    assert "fetch(" not in content or "api/" not in content, \
        "CSV↔XLSX should not call localhost API"


def test_app_js_stores_output_uri_for_open_share():
    """showResult must store uri/mime for Open/Share buttons."""
    content = APP_JS.read_text(encoding="utf-8")
    assert "currentOutputUri" in content, "Must store output URI"
    assert "currentOutputMime" in content, "Must store output MIME type"


def test_app_js_opens_with_androidbridge():
    """btn-open must use AndroidBridge.openFile, not a toast placeholder."""
    content = APP_JS.read_text(encoding="utf-8")
    assert "AndroidBridge.openFile" in content, "Open button must call native bridge"


def test_app_js_shares_with_androidbridge():
    """btn-share must use AndroidBridge.shareFile, not only Web Share API."""
    content = APP_JS.read_text(encoding="utf-8")
    assert "AndroidBridge.shareFile" in content, "Share button must call native bridge"


def test_pdf_merge_uses_pdf_lib_offline():
    """pdf-merge.js must use PDFLib (client-side), not HTTP API."""
    content = (JS_TOOLS / "pdf-merge.js").read_text(encoding="utf-8")
    assert "PDFDocument" in content, "Must use pdf-lib"
    assert "API_BASE" not in content, "Must not depend on HTTP API"


def test_pdf_split_uses_pdf_lib_offline():
    """pdf-split.js must use PDFLib (client-side), not HTTP API."""
    content = (JS_TOOLS / "pdf-split.js").read_text(encoding="utf-8")
    assert "PDFDocument" in content, "Must use pdf-lib"
    assert "API_BASE" not in content, "Must not depend on HTTP API"


def test_tool_card_delegate_click_still_present():
    """The delegated click on #tools-grid must still be present."""
    content = APP_JS.read_text(encoding="utf-8")
    assert "#tools-grid" in content or "'#tools-grid'" in content or "toolsGrid" in content, \
        "Must have tools grid element reference for delegation"
    assert "dataset.toolId" in content, "Must read data-tool-id attribute"


def test_unavailable_tools_clearly_marked():
    """Unavailable tools must show 'Unavailable' badge and reason."""
    content = APP_JS.read_text(encoding="utf-8")
    assert "badge-unavailable" in content, "Must render unavailable badge"
    assert "ANDROID_ENGINE_REASON" in content or "Not available" in content, \
        "Must explain why tool is unavailable"
