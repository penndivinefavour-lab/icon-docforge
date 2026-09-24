"""ICON DocForge - Offline-first document and file conversion engine."""
__version__ = "1.0.0"
__author__ = "Divine Favour · ICON Studios · Yaoundé, Cameroon"

from engine.registry import EngineRegistry, get_registry
from engine.utils import safe_run, validate_path, create_temp_dir, cleanup_temp, sanitize_filename, ensure_output_filename

__all__ = ["EngineRegistry", "get_registry", "safe_run", "validate_path", "create_temp_dir", "cleanup_temp", "sanitize_filename", "ensure_output_filename", "__version__", "__author__"]
