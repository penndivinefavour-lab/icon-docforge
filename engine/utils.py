"""ICON DocForge Engine Utilities."""
import os
import subprocess
import tempfile
import shutil
import re
from pathlib import Path
from datetime import datetime, timedelta
from engine.config import TEMP_DIR, OUTPUT_DIR, MAX_FILE_SIZE_BYTES, API_TIMEOUT


def validate_path(filepath: str, base_dir: str = None) -> Path:
    """Validate and sanitize a file path. Prevents directory traversal."""
    if base_dir is None:
        base_dir = str(BASE_DIR) if (BASE_DIR := os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) else str(Path(__file__).resolve().parent.parent)
    resolved = Path(filepath).resolve()
    base = Path(base_dir).resolve()
    try:
        resolved.relative_to(base)
    except ValueError:
        raise ValueError(f"Path traversal detected: {filepath}")
    return resolved


def validate_file_size(filepath: str, max_size: int = None) -> bool:
    if max_size is None:
        max_size = MAX_FILE_SIZE_BYTES
    size = os.path.getsize(filepath)
    if size > max_size:
        raise ValueError(f"File too large: {size} bytes")
    return True


def safe_run(cmd: list, timeout: int = None, capture_output: bool = True) -> dict:
    """Safely run a subprocess."""
    if timeout is None:
        timeout = API_TIMEOUT
    result = {"success": False, "stdout": "", "stderr": "", "returncode": None, "error": None}
    try:
        proc = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=timeout, shell=False)
        result["success"] = proc.returncode == 0
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
        result["returncode"] = proc.returncode
        if proc.returncode != 0:
            result["error"] = f"Exit code {proc.returncode}: {proc.stderr[:500]}"
    except subprocess.TimeoutExpired as e:
        result["error"] = f"Timed out after {timeout}s"
    except FileNotFoundError as e:
        result["error"] = f"Binary not found: {e}"
    except Exception as e:
        result["error"] = f"Error: {str(e)}"
    return result


def create_temp_dir(prefix: str = "docforge_") -> str:
    return tempfile.mkdtemp(prefix=prefix, dir=str(TEMP_DIR))


def cleanup_temp(temp_dir: str):
    if temp_dir and os.path.exists(temp_dir):
        try: shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception: pass


def get_file_info(filepath: str) -> dict:
    try:
        path = Path(filepath)
        stat = path.stat()
        return {"name": path.name, "path": str(path), "size": stat.st_size, "size_mb": round(stat.st_size / (1024*1024), 2), "exists": True}
    except Exception as e:
        return {"name": filepath, "exists": False, "error": str(e)}


def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = re.sub(r'[<>:"|?*\x00-\x1f]', '_', filename)
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    return filename


def ensure_output_filename(output_path: str, default_ext: str = ".pdf") -> str:
    path = Path(output_path)
    if not path.suffix:
        path = path.with_suffix(default_ext)
    return str(path)
