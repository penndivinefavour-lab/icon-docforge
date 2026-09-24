"""ICON DocForge Engine Capability Registry."""
import subprocess
import os
import re
from engine.config import BASE_DIR
from engine.utils import safe_run


class EngineRegistry:
    def __init__(self):
        self.engines = {}
        self._scan()
    
    def _scan(self):
        self.engines["pandoc"] = self._check("pandoc", ["pandoc", "--version"], 10, "pandoc")
        self.engines["poppler"] = self._check_poppler()
        self.engines["reportlab"] = self._check_module("reportlab", "reportlab", "python")
        self.engines["weasyprint"] = self._check_module("weasyprint", "weasyprint", "python")
        self.engines["fpdf2"] = self._check_module("fpdf2", "fpdf", "python")
        self.engines["python_docx"] = self._check_module("python-docx", "docx", "python")
        self.engines["python_pptx"] = self._check_module("python-pptx", "pptx", "python")
        self.engines["openpyxl"] = self._check_module("openpyxl", "openpyxl", "python")
        self.engines["pillow"] = self._check_module("Pillow", "PIL", "python")
        self.engines["pypdf2"] = self._check_module("PyPDF2", "PyPDF2", "python")
        self.engines["ghostscript"] = self._check("ghostscript", ["gs", "--version"], 5, "gs")
        self.engines["imagemagick"] = self._check("imagemagick", ["convert", "--version"], 5, "convert")
        self.engines["libreoffice"] = self._check("libreoffice", ["libreoffice", "--version"], 5, "libreoffice")
    
    def _check(self, name, cmd, timeout, binary):
        result = safe_run(cmd, timeout=timeout)
        if result["success"]:
            v = "unknown"
            m = re.search(r'(\d+\.\d+)', result["stdout"] + result["stderr"])
            if m: v = m.group(1)
            return {"name": name, "installed": True, "version": v, "binary": binary, "health": "healthy"}
        return {"name": name, "installed": False, "health": "not found"}
    
    def _check_module(self, name, module, kind):
        try:
            mod = __import__(module)
            v = getattr(mod, "__version__", "unknown")
            return {"name": name, "installed": True, "version": v, "health": "healthy", "module": module}
        except ImportError:
            return {"name": name, "installed": False, "health": "not found"}
    
    def _check_poppler(self):
        ok = []
        for t in ["pdftoppm", "pdftotext", "pdfunite", "pdfseparate"]:
            r = safe_run([t, "-h"], timeout=5)
            if r["success"]: ok.append(t)
        if ok:
            return {"name": "Poppler", "installed": True, "version": "26.02", "tools": ok, "health": "healthy", "capabilities": ["pdf-to-images", "pdf-merge", "pdf-split", "pdf-info", "pdf-to-text"]}
        return {"name": "Poppler", "installed": False, "health": "not found"}
    
    def get_healthy(self):
        return {k: v for k, v in self.engines.items() if v.get("installed")}
    
    def get_supported_formats(self):
        fmts = set()
        for e in self.engines.values():
            if e.get("installed"):
                fmts.update(e.get("supported_formats", set()) if isinstance(e.get("supported_formats"), (set, list)) else set())
        return sorted(fmts)
    
    def health_report(self):
        return {"product": "ICON DocForge", "version": "1.0.0", "healthy": len(self.get_healthy()), "total": len(self.engines), "engines": self.engines}
    
    def to_dict(self):
        return {"product": "ICON DocForge", "version": "1.0.0", "engine_count": len(self.engines), "healthy_count": len(self.get_healthy()), "engines": self.engines}


_registry = None
def get_registry():
    global _registry
    if _registry is None: _registry = EngineRegistry()
    return _registry
