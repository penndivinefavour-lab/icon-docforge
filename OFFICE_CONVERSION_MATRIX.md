# OFFICE_CONVERSION_MATRIX — ICON DocForge v1.2

> 本表记录所有支持/不支持的 Office 格式互转，以及每次转换的保真度评级。
> 
> **评级说明：**
> - **NATIVE** — 原生库直接读写，100% 结构保真
> - **HIGH-FIDELITY** — 通过成熟管线（Pandoc+WeasyPrint）实现，视觉与结构高度一致
> - **STRUCTURAL-RECONSTRUCTION** — 基于坐标/文本分析重建，结构大致保留，格式细节可能丢失
> - **LAYOUT-RECONSTRUCTION** — 近似布局重建，适用于图文混排场景
> - **PARTIAL** — 仅能提取部分信息（如纯文本）
> - **UNSUPPORTED** — 当前环境下技术上不可行

## 总体矩阵

| 输入\输出 | PDF | DOCX | ODT | PPTX | XLSX | ODS | CSV | HTML | TXT | MD | EPUB | PNG/JPEG |
|-----------|:---:|:----:|:---:|:----:|:----:|:---:|:---:|:----:|:---:|:--:|:------:|:--------:|
| **PDF** | — | 🔶重构 | 🔶重构 | 🔶重构 | 🔶实验 | ❌ | ❌ | 🔶重建 | 🔶重建 | ❌ | ❌ | ✅渲染 |
| **DOCX** | ✅高保真 | — | ✅原生 | 🔶语义 | ❌ | ❌ | ❌ | ✅原生 | ✅原生 | ✅原生 | ✅原生 | ❌ |
| **ODT** | ✅高保真 | ✅原生 | — | ❌ | ❌ | ❌ | ❌ | ❌ | ✅原生 | ❌ | ❌ | ❌ |
| **PPTX** | ✅高保真 | 🔶大纲 | ❌ | — | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅渲染 |
| **XLSX** | ✅高保真 | ❌ | ❌ | ❌ | — | 🔶结构 | ✅原生 | ❌ | ✅原生 | ❌ | ❌ | ❌ |
| **ODS** | ❌ | 🔶结构 | — | ❌ | 🔶结构 | — | ❌ | ❌ | ✅原生 | ❌ | ❌ | ❌ |
| **CSV** | ❌ | ✅原生 | ❌ | ❌ | ✅原生 | ❌ | — | ✅原生 | ✅原生 | ❌ | ❌ | ❌ |
| **HTML** | ✅高保真 | ✅原生 | ❌ | ❌ | ❌ | ❌ | ❌ | — | ✅原生 | ✅原生 | ❌ | ❌ |
| **TXT** | ✅高保真 | ✅原生 | ❌ | ❌ | ❌ | ❌ | ✅原生 | ✅原生 | — | ✅原生 | ❌ | ❌ |
| **Markdown** | ✅高保真 | ✅原生 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅原生 | ✅原生 | — | ❌ | ❌ |
| **Images** | ✅原生 | ❌ | ❌ | 🔶可用 | ❌ | ❌ | ❌ | ✅原生 | ❌ | ❌ | ❌ | — |

## 详细转换说明

### ✅ NATIVE / HIGH-FIDELITY（推荐优先使用）

| 转换路径 | 引擎 | 保真度 | 备注 |
|----------|------|--------|------|
| DOCX → PDF | pandoc + weasyprint | HIGH | 支持CSS样式、页眉页脚、分页符 |
| DOCX → ODT | pandoc | NATIVE | 结构无损 |
| ODT → DOCX | pandoc | NATIVE | 结构无损 |
| PPTX → PDF | pandoc | HIGH | 每幻灯片一页 |
| XLSX → PDF | openpyxl + reportlab | HIGH | 多Sheet自动分页，含列宽/表头 |
| CSV ↔ XLSX | openpyxl | NATIVE | 双向无损 |
| DOCX ↔ HTML | pandoc | NATIVE | 双向无损 |
| DOCX ↔ TXT | mammoth / docx2txt | NATIVE | 纯文本提取/生成 |
| DOCX ↔ MD | pandoc | NATIVE | Markdown往返 |
| DOCX → EPUB | pandoc | NATIVE | eBook导出 |
| TXT → DOCX/PDF | pandoc + weasyprint | HIGH | 基础格式保留 |
| Images → PDF | fpdf2 | NATIVE | 透明PNG/WebP支持 |
| PDF → Images | pdftoppm | NATIVE | 按页提取PNG |

### 🔶 STRUCTURAL / LAYOUT RECONSTRUCTION（近似重建）

| 转换路径 | 引擎 | 保真度 | 已知限制 |
|----------|------|--------|----------|
| PDF → DOCX | pdfplumber + python-docx | STRUCTURAL | 坐标定位文本，表格检测有限，无样式继承 |
| PDF → PPTX | pdfplumber + python-pptx | LAYOUT | 每页→幻灯片，文本框位置近似，图片嵌入 |
| PDF → ODT | pdfplumber + odfpy | STRUCTURAL | 类似PDF→DOCX，OpenDocument格式 |
| PDF → XLSX | pdfplumber表格检测 | EXPERIMENTAL | 仅检测规整表格，复杂布局失效 |
| PPTX → DOCX | python-pptx 大纲提取 | STRUCTURAL | 仅提取标题/正文/表格，无母版 |
| DOCX → PPTX | python-docx→pptx语义分割 | STRUCTURAL | 按Heading级别分幻灯片 |
| XLSX → ODS | openpyxl + odfpy | STRUCTURAL | 数值传递，无公式/图表 |
| ODS → XLSX | odfpy + openpyxl | STRUCTURAL | 同上 |
| PPTX → Images | reportlab渲染+pdftoppm | LAYOUT | 经PDF中转，分辨率可配置 |

### ❌ UNSUPPORTED（当前环境不可行）

| 转换路径 | 原因 |
|----------|------|
| PDF → PPTX（完全编辑） | 需理解原始演示文稿语义，当前仅能做布局重建 |
| ODT → PPTX | 无直接路径，且ODT→PPTX语义鸿沟大 |
| XLSX → PPTX | 完全不同的数据模型，无合理映射 |
| PPTX → XLSX | 同上 |
| PDF → EPUB | 缺乏结构化内容识别 |
| 任何含宏/加密文件的转换 | 安全预检会拒绝 |
| ODP → 其他 | ODF演示格式支持不足 |

---

## 保真度声明

1. **DOCX ↔ ODT**：Pandoc 转换保留绝大部分结构与样式，但仍可能有细微差异（尤其复杂表格、自定义样式）
2. **DOCX → PDF**：WeasyPrint CSS渲染与Word渲染引擎存在差异，建议以Pandoc默认模板为准
3. **PDF → Office**：本质是"重建"而非"转换"——PDF描述页面外观，不包含文档语义
4. **XLSX → PDF**：公式显示为计算值，图表不渲染，条件格式不保留
5. **PPTX → PDF**：Pandoc生成的是简化版PDF，不含动画/切换效果（这些本就不适合静态介质）

---

*最后更新：2026-09-24 · ICON DocForge v1.2.0*
