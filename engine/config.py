"""ICON DocForge Engine Configuration."""
import os
import pathlib
import tempfile

# Paths
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
ENGINE_DIR = pathlib.Path(__file__).resolve().parent
CONVERTERS_DIR = ENGINE_DIR / "converters"

OUTPUT_DIR = pathlib.Path(os.environ.get("ICONDOCFORGE_OUTPUT", str(BASE_DIR / "output")))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_DIR = pathlib.Path(os.environ.get("ICONDOCFORGE_TEMP", str(pathlib.Path(tempfile.gettempdir()) / "icon-docforge")))
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Size limits
MAX_FILE_SIZE_BYTES = int(os.environ.get("ICONDOCFORGE_MAX_INPUT_BYTES", str(500 * 1024 * 1024)))
MAX_TOTAL_TEMP_BYTES = int(os.environ.get("ICONDOCFORGE_MEMORY_LIMIT_BYTES", str(2 * 1024 * 1024 * 1024)))
MAX_CONCURRENT_JOBS = 2

# Timeouts
API_TIMEOUT = int(os.environ.get("ICONDOCFORGE_TIMEOUT", "300"))

# HTTP API
API_HOST = os.environ.get("ICONDOCFORGE_HTTP_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("ICONDOCFORGE_HTTP_PORT", "8765"))

# Product
PRODUCT_NAME = "ICON DocForge"
PRODUCT_VERSION = "1.0.0"
AUTHOR = "Divine Favour · ICON Studios · Yaoundé, Cameroon"
PRIVACY_MESSAGE = "Your files stay on your device. No documents are uploaded to any server."
DEFAULT_ONLINE_MODE = False

# Allowed extensions
ALLOWED_INPUT_EXTENSIONS = {".docx", ".md", ".txt", ".html", ".odt", ".rtf", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".csv", ".xlsx", ".xls", ".pptx", ".odp", ".ods"}
ALLOWED_OUTPUT_EXTENSIONS = {".pdf", ".docx", ".odt", ".html", ".txt", ".md", ".png", ".jpg", ".jpeg", ".tiff", ".xlsx", ".csv", ".json"}

# Create directories
for d in [OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(d, exist_ok=True)
