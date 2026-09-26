from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def test_packaged_web_entrypoint_uses_relative_assets():
    html = (WEB / "index.html").read_text(encoding="utf-8")
    assert 'src="js/app.js"' in html
    assert 'src="/js/app.js"' not in html
    assert 'href="/manifest.json"' not in html


def test_dynamic_tool_loader_uses_existing_registry_contract():
    app = (WEB / "js/app.js").read_text(encoding="utf-8")
    assert "window.DFRegistry && window.DFRegistry[toolId]" in app
    assert "script.src = `js/tools/${scriptName}.js`" in app
    assert "script.src = `/js/tools/" not in app


def test_android_tools_are_not_advertised_as_termux_backed():
    app = (WEB / "js/app.js").read_text(encoding="utf-8")
    assert "const IS_ANDROID = Boolean(window.AndroidBridge);" in app
    assert "ANDROID_ENGINE_REASON" in app


def test_registry_modules_exist_for_every_tool():
    app = (WEB / "js/app.js").read_text(encoding="utf-8")
    ids = re.findall(r"id: '([^']+)'", app[app.index("const TOOLS"): app.index("// ========== STATE")])
    aliases = {"diagnostics": "engine-diagnostic"}
    for tool_id in ids:
        module = WEB / "js/tools" / f"{aliases.get(tool_id, tool_id)}.js"
        assert module.exists(), f"Missing module for {tool_id}: {module}"


def test_no_root_relative_runtime_asset_urls():
    for path in WEB.rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"script\.src\s*=\s*`/|\bsrc:\s*['\"]/", text), path
