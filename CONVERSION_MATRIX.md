# Conversion Matrix — ICON DocForge v1.2.0

> 本表记录所有支持/不支持的格式互转，以及每次转换的保真度评级。
> 
> **评级说明：**
> - ✅ **NATIVE** — 原生库直接读写，100% 结构保真
> - 🔶 **HIGH-FIDELITY** — 通过成熟管线实现，视觉与结构高度一致
> - 🔄 **STRUCTURAL-RECONSTRUCTION** — 基于坐标/文本分析重建，结构大致保留
> - 📐 **LAYOUT-RECONSTRUCTION** — 近似布局重建
> - ❓ **EXPERIMENTAL** — 实验性功能，结果不稳定
> - ❌ **UNSUPPORTED** — 当前环境技术上不可行

---

## DOCX（Word 文档）转换矩阵

| 目标格式 | 状态 | 方法 | 保真度 | 备注 |
|---------|:----:|------|--------|------|
| → PDF | 🔶 HIGH-FIDELITY | pandoc + weasyprint + 自定义CSS | 高 | 页眉页脚、分页符、基础样式保留 |
| → ODT | ✅ NATIVE | pandoc | 高 | 结构无损，LibreOffice 兼容 |
| → HTML | ✅ NATIVE | pandoc | 高 | 含内联 CSS |
| → TXT | ✅ NATIVE | docx2txt / mammoth | 中 | 纯文本提取，丢失格式 |
| → Markdown | ✅ NATIVE | pandoc | 高 | 标准 Markdown 语法 |
| → PPTX | 🔄 STRUCTURAL | python-docx→python-pptx 语义分割 | 低 | Heading 级别→幻灯片标题 |
| → EPUB | ✅ NATIVE | pandoc | 高 | eBook 格式 |
| ← PDF | 🔄 STRUCTURAL | pdfplumber + python-docx | 低 | 坐标重建，表格有限 |
| ← ODT | ✅ NATIVE | pandoc | 高 | 双向无损 |
| ← HTML | ✅ NATIVE | pandoc | 高 | 双向无损 |
| ← Markdown | ✅ NATIVE | pandoc | 高 | 双向无损 |
| ← TXT | ✅ NATIVE | pandoc | 中 | 基础格式重建 |

---

## PDF 转换矩阵

| 目标格式 | 状态 | 方法 | 保真度 | 备注 |
|---------|:----:|------|--------|------|
| → DOCX | 🔄 STRUCTURAL | pdfplumber + python-docx | 低 | 文本+坐标重建，无样式继承 |
| → PPTX | 📐 LAYOUT | pdfplumber + python-pptx | 中 | 每页→幻灯片，文本框位置近似 |
| → ODT | 🔄 STRUCTURAL | pdfplumber + odfpy | 低 | 类似 DOCX 重建 |
| → XLSX | ❓ EXPERIMENTAL | pdfplumber 表格检测 | 极低 | 仅规整表格，复杂布局失效 |
| → PNG/JPEG | ✅ NATIVE | pdftoppm / pypdfium2 | 高 | 逐页渲染，DPI 可配 |
| → TXT | ✅ NATIVE | pdftotext | 高 | 纯文本提取 |
| ← DOCX | 🔶 HIGH-FIDELITY | pandoc + weasyprint | 高 | 推荐 DOCX→PDF 路径 |
| ← ODT | 🔶 HIGH-FIDELITY | pandoc + weasyprint | 高 | 同 DOCX |
| ← PPTX | 🔶 HIGH-FIDELITY | pandoc | 高 | 每幻灯片一页 |
| ← XLSX | 🔶 HIGH-FIDELITY | openpyxl + reportlab | 高 | 多 Sheet 分页，列宽保留 |
| ← Images | ✅ NATIVE | fpdf2 | 高 | 支持透明 PNG/WebP |

---

## PPTX（PowerPoint）转换矩阵

| 目标格式 | 状态 | 方法 | 保真度 | 备注 |
|---------|:----:|------|--------|------|
| → PDF | 🔶 HIGH-FIDELITY | pandoc | 高 | 每幻灯片一页，动画丢失 |
| → DOCX | 🔄 STRUCTURAL | python-pptx 大纲提取 | 中 | 标题/正文/表格提取 |
| → PNG/JPEG | 📐 LAYOUT | python-pptx→reportlab→pdftoppm | 中 | 经 PDF 中转渲染 |
| ← PDF | 📐 LAYOUT | pdfplumber + python-pptx | 中 | 布局重建，非完全还原 |
| ← DOCX | 🔄 STRUCTURAL | 语义分割（Heading→Slide） | 低 | 文档转演示文稿 |
| ← Images | ❌ UNSUPPORTED | — | — | 无单页→多幻灯片自动分割 |

---

## XLSX/CSV/ODS（电子表格）转换矩阵

| 目标格式 | 状态 | 方法 | 保真度 | 备注 |
|---------|:----:|------|--------|------|
| → PDF | 🔶 HIGH-FIDELITY | openpyxl + reportlab | 高 | 多 Sheet 分页，表头重复 |
| → CSV | ✅ NATIVE | openpyxl | 高 | 纯数据导出 |
| → ODS | 🔄 STRUCTURAL | openpyxl + odfpy | 中 | 数值传递，无公式/图表 |
| ← CSV | ✅ NATIVE | openpyxl | 高 | 双向无损 |
| ← ODS | 🔄 STRUCTURAL | odfpy + openpyxl | 中 | 数值传递 |
| ← PDF | ❓ EXPERIMENTAL | pdfplumber 表格检测 | 极低 | 仅规整表格可行 |
| → DOCX/PPTX | ❌ UNSUPPORTED | — | — | 数据模型不匹配 |

---

## ODF（OpenDocument）转换矩阵

| 目标格式 | 状态 | 方法 | 保真度 | 备注 |
|---------|:----:|------|--------|------|
| ODT → PDF | 🔶 HIGH-FIDELITY | pandoc + weasyprint | 高 | 标准文档流程 |
| ODT → DOCX | ✅ NATIVE | pandoc | 高 | 双向无损 |
| ODS → XLSX | 🔄 STRUCTURAL | odfpy + openpyxl | 中 | 数值+基础格式 |
| ODP → PDF | ❌ UNSUPPORTED | — | — | 无有效渲染器 |
| ODP → PPTX | ❌ UNSUPPORTED | — | — | 无有效转换路径 |

---

## 图片格式转换矩阵

| 目标格式 | 状态 | 方法 | 保真度 | 备注 |
|---------|:----:|------|--------|------|
| → PDF | ✅ NATIVE | fpdf2 | 高 | 支持多页、A4/Letter/原尺寸 |
| → DOCX | ❌ UNSUPPORTED | — | — | 需先转 PDF 再转 DOCX |
| PNG ↔ JPEG | ✅ NATIVE | Pillow | 高 | 质量可配 |
| PNG ↔ WebP | ✅ NATIVE | Pillow | 高 | 支持透明通道 |
| → TIFF | ✅ NATIVE | Pillow | 高 | 无损压缩选项 |

---

## 文本/标记语言转换矩阵

| 目标格式 | 状态 | 方法 | 保真度 | 备注 |
|---------|:----:|------|--------|------|
| Markdown → PDF | 🔶 HIGH-FIDELITY | pandoc + weasyprint | 高 | 支持表格、代码块 |
| Markdown → DOCX | ✅ NATIVE | pandoc | 高 | 双向无损 |
| HTML → DOCX | ✅ NATIVE | pandoc | 高 | 双向无损 |
| HTML → PDF | 🔶 HIGH-FIDELITY | weasyprint | 高 | 完整 CSS 支持 |
| TXT → DOCX/PDF | ✅ NATIVE | pandoc | 高 | 基础格式 |

---

## 无法实现的转换（技术限制）

| 转换路径 | 原因 |
|---------|------|
| PDF → 可编辑 DOCX（高保真） | PDF 是布局描述，不含文档语义；重建结果近似 |
| PPTX → 带动画 PDF | 静态介质无法承载动画，仅输出最终帧 |
| XLSX → PPTX / DOCX → PPTX | 数据模型完全不同，无合理映射 |
| ODP → 任何格式 | Termux 无 ODP 渲染引擎，LibreOffice 体积过大 |
| 含宏/加密文件转换 | 安全预检拒绝处理 |
| 复杂公式/图表保留 | 当前库不支持 MathML/图表序列化 |

---

## 引擎版本清单

| 组件 | 版本 | 许可证 | 用途 |
|------|------|--------|------|
| Pandoc | 3.11 | GPL-2.0+ | 格式转换核心 |
| WeasyPrint | 69.0 | BSD | CSS→PDF 渲染 |
| ReportLab | 5.0 | BSD | Python PDF 生成 |
| python-docx | 1.2.0 | MIT | DOCX 读写 |
| python-pptx | 1.0.2 | MIT | PPTX 读写 |
| openpyxl | 3.1.5 | MIT | XLSX 读写 |
| PyPDF2 | 3.0.1 | BSD | PDF 元数据/合并/拆分 |
| pdfplumber | 0.11.10 | MIT | PDF 文本/表格提取 |
| pypdfium2 | 5.13.0 | Apache-2.0 | PDF 图像渲染 |
| fpdf2 | 2.8.8 | MIT | 图像→PDF |
| odfpy | 1.4.1 | LGPL | ODF 格式支持 |
| mammoth | 1.12.2 | MIT | DOCX→纯文本 |
| docx2txt | 0.9 | Apache-2.0 | DOCX→纯文本 |
| Pillow | 12.3.0 | HPND | 图像处理 |

---

*最后更新：2026-09-24 · ICON DocForge v1.2.0*
*隐私声明：所有转换在设备本地完成，无数据上传*
