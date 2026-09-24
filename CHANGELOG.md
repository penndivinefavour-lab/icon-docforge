# ICON DocForge v1.2.0 发布说明

## 新增功能

### Office 文档转换（核心升级）

**DOCX 增强：**
- DOCX → PDF（带自定义 CSS 样式的专业排版）
- DOCX → ODT（LibreOffice 格式）
- DOCX → HTML（网页格式）
- DOCX → TXT（纯文本提取）
- DOCX → Markdown（标记语言）
- DOCX → EPUB（电子书格式）
- DOCX → PPTX（语义分割为演示文稿）

**PDF 增强：**
- PDF → DOCX（坐标解析重建）
- PDF → PPTX（每页→幻灯片，混合模式）
- PDF → ODT（OpenDocument 格式）
- PDF → XLSX（实验性表格检测）
- PDF → 文本提取（带页码定位）
- PDF 水印添加（元数据级）
- PDF 压缩（72 DPI 重渲染）
- PDF 页面重排序/删除

**PPTX 增强：**
- PPTX → PDF（每幻灯片一页）
- PPTX → PNG/JPEG 序列（经 PDF 中转）
- PPTX → DOCX（大纲提取）
- PPTX → 图片（坐标渲染）

**电子表格增强：**
- XLSX → PDF（多 Sheet 分页，表头重复）
- XLSX → ODS（OpenDocument 格式）
- ODS → XLSX
- PDF → XLSX（实验性表格检测）

**ODF 格式支持：**
- ODT → PDF（pandoc + weasyprint）
- ODT → DOCX（pandoc 双向无损）
- ODS → XLSX（数值+基础格式）

**文本/标记语言：**
- Markdown → PDF（完整样式）
- Markdown → DOCX
- HTML → DOCX / HTML → PDF
- TXT → DOCX / TXT → PDF

### 新工具模块

- `engine/office_support.py`：预检、验证、字体发现
- `engine/converters/docx_convert.py`：DOCX 多格式转换
- `engine/converters/docx_to_pdf_v2.py`：带 CSS 样式的 PDF 生成
- `engine/converters/pptx_convert.py`：PPTX 全套转换
- `engine/converters/spreadsheet_pdf.py`：电子表格与 PDF 互转
- `engine/converters/pdf_to_office.py`：PDF 到 Office 格式重建

### CLI 扩展

```bash
iconconvert convert input.docx --to pdf      # DOCX→PDF
iconconvert convert input.pptx --to pdf      # PPTX→PDF
iconconvert convert input.xlsx --to pdf      # XLSX→PDF
iconconvert convert input.pdf --to docx      # PDF→DOCX
iconconvert office-status                    # 查看 Office 支持状态
iconconvert doctor                           # 引擎健康检查
```

### 测试覆盖

- **55/55 测试全部通过**
- 新增 Office 格式转换测试
- 新增 round-trip 往返测试
- 新增 Unicode 文件名测试
- 新增预检/验证测试

---

## 已知限制

### 技术上不可行（Termux 环境）

| 功能 | 原因 |
|------|------|
| Ghostscript | Termux 仓库无此包 |
| ImageMagick | aarch64 架构不兼容 |
| LibreOffice | ~500MB+，Pixel 4a 内存不足 |
| QPDF | Termux 仓库无此包 |
| Tesseract OCR | 仅对扫描件有意义，当前未安装 |
| ODP → PDF/PPTX | 无有效渲染器 |

### 保真度限制

- **PDF → Office**：本质是"重建"而非"转换"，结果近似
- **复杂表格/公式**：仅保留结构，样式可能丢失
- **PPTX 动画**：静态介质无法承载，仅输出最终帧
- **Excel 公式**：显示为缓存值，不重新计算

---

## 隐私与安全

- ✅ 所有转换在设备本地完成
- ✅ HTTP API 绑定 127.0.0.1，不暴露公网
- ✅ 无遥测、无 analytics、无第三方服务
- ✅ 宏/OLE 对象安全预检并拒绝执行
- ✅ 加密 PDF 需密码解锁

---

## 安装方式

### Termux
```bash
pkg install pandoc poppler utils python
pip install weasyprint reportlab python-docx python-pptx openpyxl \
            PyPDF2 pdfplumber pypdfium2 fpdf2 odfpy mammoth docx2txt Pillow
cd "/data/data/com.termux/files/home/ICON Studios 2026/ICON DocForge"
python3 engine/cli.py doctor
```

### Android APK（待构建）
通过 GitHub Actions 远程构建，或本地使用 Capacitor。

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.0.0 | 2026-09-24 | 初始发布，基础 PDF/DOCX/Image 转换 |
| v1.1.0 | 2026-09-24 | PDF 增强（文本提取、搜索、压缩、水印） |
| v1.2.0 | 2026-09-24 | **Office 全格式支持**，55 项测试通过 |

---

*ICON Studios · Divine Favour · Yaoundé, Cameroon*
*GitHub: https://github.com/penndivinefavour-lab/icon-docforge*
