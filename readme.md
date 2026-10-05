
# 📘 **notion-paper-automation**

### *An AI-powered Notion literature management system*

（自动化文献解析 → 分类 → 结构化笔记 → 写入 Notion）

---

## Maintainer

**Liang Yu**  
Chinese Academy of Medical Sciences & Peking Union Medical College  
GitHub: [@LianaSakana001](https://github.com/LianaSakana001)  
ORCID: [0009-0002-2054-7620](https://orcid.org/0009-0002-2054-7620)

## 🚀 项目简介

**notion-paper-automation** 是一个基于 **Python + Notion API + LLM** 的自动化文献管理工具。

它可以：

* 自动读取 PDF / Zotero / 手动输入的论文内容
* 自动用大语言模型（LLM）抽取结构化信息
* 自动判断文献类型（AI、生物学、组学、综述、其他，可多选）
* 自动生成标准化文献笔记
* 自动写入你的 Notion 文献数据库

只需运行一行命令，就能瞬间将论文转化为整理好的 Notion 条目。

---

## 🧩 特性（Features）

### ✔ **1. 手动模式（推荐）**

用户与 AI 对话，生成：

```python
papers = [ {...} ]
```

然后运行：

```
python main.py
```

自动写入 Notion。

---

### ✔ **2. 批量模式：Zotero 自动读取（可选）**

```
python -m batch_mode.batch_run
```

功能：

* 从 Zotero collection 自动读取文献
* 自动下载 PDF（含本地缓存支持）
* 自动解析 PDF → 结构化 JSON
* 自动写入 Notion

---

### ✔ **3. 批量模式：本地 PDF 文件夹（强烈推荐）**

```
python -m batch_mode.batch_run_localpdf
```

功能：

* 遍历 `local_pdfs/` 下所有 PDF
* 自动解析、分类、生成结构化笔记
* 自动写入 Notion

无需 Zotero！简单、快速、纯本地。

---

### ✔ **4. 支持多类别分类体系（AI 自动判断）**

每篇文献可同时属于多个类别，例如：

* `"AI + 生物医学 (算法类)"`
* `"生物医学/机制研究 (Wet Lab)"`
* `"组学/图谱/多组学"`
* `"综述"`（Review）
* `"其他"`（无法归类时）

支持任意组合：

```python
"categories": ["AI + 生物医学 (算法类)", "组学/图谱/多组学"]
```

---

### ✔ **5. 高度可扩展 + 完全隐私安全**

* 所有密钥存放 `.env`，不进入代码
* 支持任意 LLM（OpenAI / SiliconFlow / DeepSeek）
* 代码无硬编码路径
* 完全适合公开分享与协作

---

## 📦 安装（Installation）

### **1. 克隆仓库**

```
git clone https://github.com/yourname/notion-paper-automation.git
cd notion-paper-automation
```

### **2. 安装依赖**

```
pip install -r requirements.txt
```

### **3. 配置 `.env`**

复制模板：

```
cp .env.example .env
```

并填写：

* Notion Token
* Notion Database ID
* LLM API Key（OpenAI 或 SiliconFlow）
* Zotero API（可选）

---

## 🛠 使用方法（Usage）

---

# **方式一：手动模式（与 AI 交互）**

1. 与 ChatGPT/DeepSeek/Qwen 对话，生成

   ```python
   papers = [ {...} ]
   ```
2. 将内容粘贴进：

```
papers_to_add_example.py
```

3. 运行：

```
python main.py
```

🎉 文献将自动写入 Notion。

---

# **方式二：本地 PDF 自动解析（推荐）**

1. 将 PDF 放入：

```
local_pdfs/
```

2. 运行：

```
python -m batch_mode.batch_run_localpdf
```

LLM 将自动读取 PDF → 解析 → 写入 Notion。

---

# **方式三：Zotero 批量导入（可选）**

配置 Zotero API 后运行：

```
python -m batch_mode.batch_run
```

系统会：

* 扫描 Zotero collection
* 自动下载 PDF
* 自动解析
* 自动写入 Notion

---

## 📚 文献 Schema（AI 自动生成时必须遵守）

### 公共字段（所有文章都必须填写）

* `title`
* `journal`
* `doi`
* `date`
* `summary`
* `key_conclusions`
* `limitations`
* `study_type`
* `disease`
* `aim`
* `categories`（多选，必填）

### 分类类型（自动判断）

* `"AI + 生物医学 (算法类)"`
* `"生物医学/机制研究 (Wet Lab)"`
* `"组学/图谱/多组学"`
* `"综述"`
* `"其他"`

### AI 类字段

* `task_type`
* `metrics`
* `architecture`
* `data_source`
* 等等

### Wet Lab 字段

* `species_model`
* `sample_size`
* `key_techniques`
* …

### 组学字段

* `omics_data_type`
* `analysis_workflow`
* …

所有字段在 `notion_utils.py` 中有完整定义。

---

## 📁 项目结构（Project Structure）

```
notion-paper-automation/
│
├── main.py
├── notion_utils.py
├── papers_to_add_example.py
│
├── batch_mode/
│   ├── batch_run.py
│   ├── batch_run_localpdf.py
│   └── config.py
│
├── local_pdfs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔒 隐私与安全（Privacy & Safety）

* `.env` 不会被提交
* 密钥全部由用户自行设置
* 除公开的维护者署名外，不提交私人信息或访问凭据
* 支持本地 PDF 处理，无需上传到云

适合科研人员、学生、团队内部使用。

---

## 📄 License

本项目采用 **MIT License**，允许自由使用、修改、商用。

---

## ❤️ 贡献（Contributing）

欢迎提交 PR、Issue：

* 新增文献分类
* 改进 LLM prompt
* 增加新的批量处理方式
* 支持更多学科领域

---

# 🎉 完成！
