# OFFICE ENGINE RESEARCH — ICON DocForge v1.2

## 一、调查结论概述

经过系统性调研与实测，确认在 Android/Termux 环境（aarch64）下可实现以下 Office 格式转换：

- ✅ **完全可行**：DOCX/ODT/PPTX/XLSX 互转（通过 Pandoc + 各语言库）
- ✅ **高保真 PDF**：Pandoc + WeasyPrint 管线可输出带样式的 PDF
- ✅ **PDF→Office**：pdfplumber 坐标解析 + python-docx/pptx/openpyxl 重建
- ❌ **不可行**：LibreOffice/QPDF/Ghostscript/ImageMagick（无 Termux 包或体积过大）
- ⚠️ **近似/重建**：所有 PDF→Office 均为结构重建，非像素级还原

---

## 二、引擎清单与来源

| 引擎 | 版本 | 来源 | 许可证 | 用途 |
|------|------|------|--------|------|
| **Pandoc** | 3.11 | Termux repo (`pkg install pandoc`) | GPL-2.0+ | DOCX↔MD↔HTML↔PPTX↔PDF |
| **WeasyPrint** | 69.0 | pip | BSD | HTML→PDF（CSS渲染引擎） |
| **ReportLab** | 5.0 | pip | BSD | Python原生PDF生成（PPTX渲染、XLSX→PDF） |
| **python-docx** | 1.2.0 | pip | MIT | DOCX读写 |
| **python-pptx** | 1.0.2 | pip | MIT | PPTX读写/生成 |
| **openpyxl** | 3.1.5 | pip | MIT | XLSX读写 |
| **pypdf2** | 3.0.1 | pip | BSD | PDF元数据、合并/拆分 |
| **pdfplumber** | 0.11.10 | pip | MIT | PDF文本/表格提取（新） |
| **pypdfium2** | 5.13.0 | pip | Apache-2.0 | PDF渲染图片（新） |
| **odfpy** | 1.4.1 | pip (via pdf2docx) | LGPL | ODT/ODS读写（新） |
| **mammoth** | 1.12.2 | pip | MIT | DOCX→纯文本（新） |
| **docx2txt** | 0.9 | pip | Apache-2.0 | DOCX→纯文本（新） |

### 明确不可用（已验证）

| 引擎 | 原因 |
|------|------|
| **Ghostscript** | Termux仓库无此包；Android Bionic libc 兼容性差 |
| **ImageMagick** | aarch64 Termux 仓库中不存在 |
| **LibreOffice** | 体积 ~500MB+，需要完整 JVM/GTK 依赖链，Pixel 4a 无法承受 |
| **QPDF** | Termux 仓库中不存在 |
| **Tesseract OCR** | Termux 仓库中不存在；仅对扫描件有意义 |
| **pdf2docx (原路径)** | PyMuPDF 依赖太大（~88MB源码编译），Pixel 4a 内存不足 |

---

## 三、关键发现

### 3.1 Pandoc 的意外能力
Pandoc 3.11 支持 **PPTX 作为输入格式**（`--list-input-formats` 含 `pptx`），可直接：
- `pandoc input.pptx -o output.pdf` → 生成 PDF
- `pandoc input.pptx -o output.docx` → 转换为 DOCX
- `pandoc input.docx -o output.pptx` → **语义转换**为 PPTX

这意味着我们不需要 LibreOffice 即可实现大部分 PPTX↔其他格式转换。

### 3.2 pdfplumber + pypdfium2 组合
- **pdfplumber**：提取 PDF 文本坐标、表格结构（基于 pdfminer.six）
- **pypdfium2**：将 PDF 页面渲染为 PNG（基于 Chromium 渲染引擎）
- 两者结合可实现：PDF→坐标感知 Office 文档重建

### 3.3 字体策略
Termux 自带 230 个字体文件，DejaVu 系列完整（Sans/Serif/Mono）。
WeasyPrint 自动 fallback 到 DejaVu，无需额外安装。

### 3.4 Excel 公式处理
openpyxl 以 `data_only=True` 加载时只读取**缓存值**，不执行公式。
生成的 XLSX/ODS 中公式丢失——这在文档中明确标注。

---

## 四、架构决策

```
┌─────────────────────────────────────────────────────┐
│  用户请求 (Web/API/CLI)                              │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  预检阶段 (office_support.preflight)                  │
│  · 检查文件是否存在                                  │
│  · 扫描宏/OLE对象（标记风险）                         │
│  · 检测加密PDF                                       │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  路由决策                                            │
│  · 格式匹配 → 选择对应转换器                          │
│  · 未支持 → 返回 UNSUPPORTED + 建议                   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  转换执行层                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Pandoc管线   │ │ Python库管线 │ │ Poppler管线  │   │
│  │ (subprocess)│ │ (in-process) │ │ (subprocess)│   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  后处理 & 验证                                       │
│  · validate_docx/xlsx/pptx/pdf                      │
│  · 清理临时文件                                      │
│  · 返回结果 + 元数据（fidelity/method/notes）         │
└─────────────────────────────────────────────────────┘
```

---

## 五、v1.2 新增转换器

| 模块 | 函数 | 功能 |
|------|------|------|
| `docx_convert.py` | `docx_to_html()` | DOCX→HTML |
| | `html_to_docx()` | HTML→DOCX |
| | `docx_to_txt()` | DOCX→纯文本 |
| | `txt_to_docx()` | 纯文本→DOCX |
| | `docx_to_markdown()` | DOCX→Markdown |
| | `markdown_to_docx()` | Markdown→DOCX |
| | `docx_to_epub()` | DOCX→EPUB |
| `docx_to_pdf_v2.py` | `docx_to_pdf()` | DOCX→PDF（带CSS样式） |
| | `odt_to_pdf()` | ODT→PDF |
| | `txt_to_pdf()` | TXT→PDF |
| | `pdf_to_odt()` | PDF→ODT（重建） |
| `pptx_convert.py` | `pptx_to_pdf()` | PPTX→PDF（坐标渲染） |
| | `pptx_to_images()` | PPTX→PNG序列 |
| | `pptx_to_docx()` | PPTX→DOCX（大纲提取） |
| | `docx_to_pptx()` | DOCX→PPTX（语义分割） |
| `pdf_to_office.py` | `pdf_to_docx()` | PDF→DOCX（坐标重建） |
| | `pdf_to_pptx()` | PDF→PPTX（混合模式） |
| `spreadsheet_pdf.py` | `xlsx_to_pdf()` | XLSX→PDF（多Sheet分页） |
| | `pdf_to_xlsx()` | PDF→XLSX（表格检测） |
| | `xlsx_to_ods()` | XLSX→ODS |
| | `ods_to_xlsx()` | ODS→XLSX |
| `office_support.py` | `preflight()` | 文件安全预检 |
| | `validate_docx/xlsx/pptx/pdf()` | 输出验证 |
| | `discover_fonts()` | 字体发现 |
| | `pick_fallback()` | 字体回退选择 |
