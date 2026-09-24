# Termux Setup Guide

Complete guide to installing and running ICON DocForge on Android via Termux.

## Prerequisites

1. **Install Termux** from [F-Droid](https://f-droid.org/en/packages/com.termux/) (NOT the Play Store version — it's outdated and lacks package support)
2. **Grant storage access**: `termux-setup-storage`
3. **Grant microphone** (for any audio-related features in future)

## Step-by-Step Installation

### Step 1: Update Termux

```bash
pkg update && pkg upgrade -y
```

### Step 2: Install Python and Pip

```bash
pkg install python python-pip -y
```

### Step 3: Install Python Packages

```bash
pip install pdf2docx python-docx python-pptx openpyxl Pillow pymupdf flask
```

Or if you have a `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Step 4: Clone the Repository

```bash
git clone https://github.com/penndivinefavour-lab/icon-docforge.git
cd icon-docforge
```

### Step 5: Verify Installation

```bash
python3 --version
python3 -c "import pdf2docx, docx, pptx, openpyxl, PIL, fitz, flask; print('All dependencies OK')"
```

### Step 6: Run the Engine

```bash
# Start the local server with web UI:
python3 engine.py --server --port 8080

# Or use CLI mode directly:
python3 engine.py --input document.pdf --output document.docx --from pdf --to docx
```

### Step 7: Access the Web UI

Open any browser on your Android device and navigate to:

```
http://127.0.0.1:8080
```

Or from another device on the same network:

```
http://<your-device-ip>:8080
```

> **Note**: The server binds to `127.0.0.1` by default (localhost only). To allow network access, use `--host 0.0.0.0`.

---

## Useful Termux Commands

```bash
# Check if packages are installed:
pip list | grep -E "pdf2docx|python-docx|python-pptx|openpyxl|Pillow|pymupdf|flask"

# Update all Python packages:
pip install --upgrade pdf2docx python-docx python-pptx openpyxl Pillow pymupdf flask

# Run in background (using termux-thermostat or &):
python3 engine.py --server --port 8080 &

# Stop the server:
pkill -f "engine.py"

# Check running processes:
pgrep -f "engine.py"
```

---

## Keyboard Shortcuts (Termux)

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Stop the server |
| `Tab` | Auto-complete |
| `Ctrl+L` | Clear screen |
| `Volume Up + L` | Toggle terminal layout |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'pdf2docx'`

```bash
pip install pdf2docx
```

If pip fails, try:

```bash
pip install --user pdf2docx
```

### `Permission denied` when writing files

You need storage access:

```bash
termux-setup-storage
```

Then grant the permission in the popup. Files will be accessible at `/sdcard/`.

### Port 8080 already in use

```bash
# Check what's using port 8080:
netstat -tlnp | grep 8080

# Kill the process:
pkill -f "python.*8080"

# Or use a different port:
python3 engine.py --server --port 8081
```

### Slow conversion

- Large files (>20MB) take longer
- Close other apps to free RAM
- Ensure you're not running on battery saver mode

### `python: not found`

```bash
pkg install python
```

---

## Auto-start on Boot

Create a script to auto-start the server:

```bash
# Create startup script:
cat > ~/.termux/boot/docforge.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd /data/data/com.termux/files/home/icon-docforge
python3 engine.py --server --port 8080 &
EOF

chmod +x ~/.termux/boot/docforge.sh
```

---

## Updating

```bash
cd icon-docforge
git pull origin main
pip install --upgrade pdf2docx python-docx python-pptx openpyxl Pillow pymupdf flask
```

---

## Uninstalling

```bash
# Remove the package:
pip uninstall pdf2docx python-docx python-pptx openpyxl Pillow pymupdf flask

# Remove the project:
rm -rf ~/icon-docforge
```

---

## Performance Tips

1. **Close background apps** before large conversions
2. **Use Wi-Fi** if downloading dependencies
3. **Keep Termux updated**: `pkg update && pkg upgrade`
4. **Use a swap file** if you have many conversions: `fallocate -l 1G /data/data/com.termux/files/home/swapfile && mkswap swapfile && swapon swapfile`
