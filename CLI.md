# CLI Reference

## Usage

```bash
python3 engine.py [OPTIONS]
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--input FILE` | `-i` | Input file path |
| `--output FILE` | `-o` | Output file path |
| `--from FORMAT` | `-f` | Input format (pdf, docx, pptx, xlsx, csv, png, jpg, webp, txt) |
| `--to FORMAT` | `-t` | Output format |
| `--batch FILE` | `-b` | Batch configuration JSON file |
| `--server` | `-s` | Start local HTTP server with web UI |
| `--port PORT` | `-p` | Port for HTTP server (default: 8080) |
| `--host HOST` | `-H` | Host for HTTP server (default: 127.0.0.1) |
| `--log LEVEL` | `-l` | Log level (debug, info, warning, error) |
| `--timeout SECONDS` | `-T` | Conversion timeout in seconds (default: 300) |
| `--help` | `-h` | Show help message |
| `--version` | `-v` | Show version |

## Examples

### Single File Conversion
```bash
python3 engine.py --input report.pdf --output report.docx --from pdf --to docx
```

### Convert with Custom Output Path
```bash
python3 engine.py -i document.pdf -o /sdcard/Documents/document.docx -f pdf -t docx
```

### Start Web Server
```bash
python3 engine.py --server --port 8080
```

### Batch Conversion
```bash
python3 engine.py --batch conversions.json
```

Batch JSON format:
```json
{
  "jobs": [
    {
      "input": "file1.pdf",
      "output": "file1.docx",
      "from": "pdf",
      "to": "docx"
    },
    {
      "input": "data.xlsx",
      "output": "data.pdf",
      "from": "xlsx",
      "to": "pdf"
    }
  ]
}
```

### Run with Debug Logging
```bash
python3 engine.py --server --port 8080 --log debug
```

### Set Custom Timeout
```bash
python3 engine.py --input large_file.pdf --output large_file.docx --from pdf --to docx --timeout 600
```

## Server API

When running with `--server`, the following HTTP endpoints are available:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web UI home page |
| `GET` | `/formats` | JSON list of supported formats |
| `POST` | `/convert` | Start a conversion |
| `GET` | `/status/:id` | Get conversion status |
| `GET` | `/download/:id` | Download converted file |
| `GET` | `/health` | Health check |

### POST /convert Request Body
```json
{
  "input_path": "/path/to/input.pdf",
  "output_path": "/path/to/output.docx",
  "from_format": "pdf",
  "to_format": "docx"
}
```

### Response Format
```json
{
  "status": "success",
  "job_id": "abc123",
  "input": "input.pdf",
  "output": "output.docx",
  "from": "pdf",
  "to": "docx",
  "size": 1024000,
  "message": "Conversion complete"
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCFORGE_PORT` | `8080` | Default server port |
| `DOCFORGE_HOST` | `127.0.0.1` | Default server host |
| `DOCFORGE_TIMEOUT` | `300` | Default conversion timeout in seconds |
| `DOCFORGE_TMP_DIR` | `/tmp/docforge` | Temporary directory for conversions |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Format not supported |
| 5 | Conversion timeout |
| 6 | Permission denied |
