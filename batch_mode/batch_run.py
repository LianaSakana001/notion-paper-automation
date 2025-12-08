# batch_mode/batch_run.py

import json
import textwrap
import shutil
import os
import traceback
from pathlib import Path

from pyzotero import zotero
import fitz  # PyMuPDF
from openai import OpenAI

from .config import (
    ZOTERO_API_KEY,
    ZOTERO_LIBRARY_ID,
    ZOTERO_LIBRARY_TYPE,
    ZOTERO_COLLECTION_KEY,
    MAX_ITEMS,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_BASE_URL,
    OUTPUT_PY_PATH,
    MAX_PDF_PAGES,
)


def debug(msg: str):
    print(f"[batch_mode] {msg}")


def get_zotero_client():
    debug("初始化 Zotero 客户端...")
    if not ZOTERO_API_KEY or not ZOTERO_LIBRARY_ID:
        raise ValueError("Zotero 配置缺失，请在 .env 中设置 ZOTERO_API_KEY 和 ZOTERO_LIBRARY_ID")
    return zotero.Zotero(ZOTERO_LIBRARY_ID, ZOTERO_LIBRARY_TYPE, ZOTERO_API_KEY)


def fetch_items_from_collection(zot):
    debug(f"从 collection {ZOTERO_COLLECTION_KEY} 获取条目（最多 {MAX_ITEMS} 篇）...")
    items = zot.collection_items(ZOTERO_COLLECTION_KEY, limit=MAX_ITEMS)
    debug(f"获取到 {len(items)} 条条目")
    return items


def get_pdf_attachment(zot, item):
    """从 Zotero 条目中找到 PDF 附件（如果有）"""
    attachments = zot.children(item["key"])
    for child in attachments:
        if child["data"].get("contentType", "").lower() == "application/pdf":
            return child
    return None


def download_pdf(zot, attachment, download_dir="batch_mode_tmp"):
    """优先从本地 Zotero storage 找 PDF；找不到再尝试云端下载"""
    download_path = Path(download_dir)
    download_path.mkdir(exist_ok=True)
    filename = f'{attachment["key"]}.pdf'
    target_file_path = download_path / filename

    # 已存在则直接使用
    if target_file_path.exists():
        debug(f"PDF 已存在于临时目录，直接使用：{target_file_path}")
        return target_file_path

    # 从本地 Zotero storage 尝试复制
    user_home = Path.home()
    local_storage_path = user_home / "Zotero" / "storage" / attachment["key"]

    if local_storage_path.exists():
        for file in local_storage_path.iterdir():
            if file.suffix.lower() == ".pdf":
                debug(f"✅ 在本地 Zotero storage 找到 PDF，复制中：{file.name}")
                shutil.copy(file, target_file_path)
                return target_file_path

    # 云端下载（前提是同步 & 有空间）
    debug("本地未找到，尝试从云端下载 PDF ...")
    try:
        zot.dump(attachment["key"], str(target_file_path))
    except Exception as e:
        debug(f"⚠ 云端下载失败 (可能未同步或空间已满): {e}")
        if target_file_path.exists():
            target_file_path.unlink()
        raise e

    return target_file_path


def extract_pdf_text(pdf_path: Path, max_pages: int = MAX_PDF_PAGES) -> str:
    debug(f"从 PDF 提取文本：{pdf_path}（最多 {max_pages} 页）")
    doc = fitz.open(pdf_path)
    texts = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        texts.append(page.get_text())
    text = "\n".join(texts)
    debug(f"提取文本长度：{len(text)} 字符")
    return text


def build_system_prompt() -> str:
    """
    使用【多类别 + 综述/其他】新 Schema，指导 LLM 输出 JSON:
    { "papers": [ { ... } ] }
    """
    prompt = textwrap.dedent(
        """
        你是一个文献结构化助手。请根据文献内容生成符合 Schema 的 JSON。

        =========================
        一、文献分类体系（多选）
        =========================

        字段名为 "categories"，类型为【字符串列表】，而不是单个字符串。

        技术类（可多选）：
        1. "AI + 生物医学 (算法类)"
        2. "生物医学/机制研究 (Wet Lab)"
        3. "组学/图谱/多组学"

        特殊类（单独使用）：
        4. "综述"
        5. "其他"

        规则：
        - 原创研究：
            - 如果是 AI 文章：categories 至少包含 "AI + 生物医学 (算法类)"
            - 如果涉及 Wet Lab 实验：可以再加 "生物医学/机制研究 (Wet Lab)"
            - 如果涉及组学 / 图谱 / 多组学分析：可以再加 "组学/图谱/多组学"
            - 允许 1~3 个技术类同时出现，例如：
              ["AI + 生物医学 (算法类)", "组学/图谱/多组学"]

        - 综述文章：
            - 如果主要是综述（review），没有自己新的实验 / 模型：
              只使用：["综述"]
            - 不要再额外加 AI / Wet Lab / 组学 标签

        - 其他文章：
            - 如果既不是 AI 文章、也不属于 Wet Lab 或组学类，也不是综述：
              使用：["其他"]

        =========================
        二、字段要求
        =========================

        每篇文献必须返回一个完整对象，字段分为：

        1）公共字段：
            - categories        : 列表，见上（至少 1 个元素）
            - title             : 标题
            - journal           : 期刊
            - doi               : DOI（无则 "N/A"）
            - date              : 发表时间（尽量 YYYY-MM-DD，未知可 "N/A"）
            - study_type        : 研究类型（方法开发 / 机制研究 / 图谱构建 / 综述 等）
            - summary           : 一句话总结
            - key_conclusions   : 关键结论（可多点，用一个字符串概括）
            - limitations       : 局限性与未来方向
            - disease           : 研究疾病（如 "Alzheimer's disease"，不聚焦疾病可 "Other" 或 "N/A"）
            - aim               : 研究目的（这篇文章想解决的核心问题）

        2）AI + 生物医学（算法类）专属字段：
            - task_type         : 任务类型（诊断 / 分割 / 预后 / 生存预测 等）
            - bio_relevance     : 生物学/临床意义
            - metrics           : 主要评价指标（AUC, F1, Dice 等）
            - architecture      : 算法/模型架构（CNN, Transformer, GNN 等）
            - data_source       : 数据来源与获取（如 ADNI, TCGA, 单中心队列）
            - code_hardware     : 代码开源情况与算力需求

        3）生物医学/机制研究（Wet Lab）专属字段：
            - species_model     : 物种与模型（human, mouse, specific strain 等）
            - sample_size       : 样本量统计（如 "n=10 mice per group"）
            - key_techniques    : 关键实验技术列表（如 ["IHC", "Western blot"]）
            - target_pathway    : 核心通路/分子
            - validation        : 验证实验设计（体内/体外/救援实验等）

        4）组学 / 图谱 / 多组学 专属字段：
            - omics_data_type   : 组学数据类型（scRNA-seq, snRNA-seq + snATAC-seq 等）
            - sample_details    : 样本详情（数量、组织来源、疾病/对照等）
            - cell_types        : 注释到的主要细胞类型/分群
            - analysis_workflow : 主要分析流程（质控 → 降维 → 聚类 → 注释 → 差异分析 等）
            - innovative_methods: 是否引入新的分析方法/算法
            - reproducibility   : 可重复性信息（公开数据/代码/流程等）

        =========================
        三、综述 & 其他 的特殊要求
        =========================

        - 如果 categories = ["综述"] 或 ["其他"]：
            - 只需要认真填写公共字段
            - 以上所有专属字段仍然必须出现，但可以统一填 "N/A"

        - 如果是原创研究（包含任意技术类标签）：
            - 公共字段必须填写
            - 对应到的技术类字段应尽量填写清晰；与该文献无关的技术块字段可以填 "N/A"

        =========================
        四、输出格式
        =========================

        必须输出一个严格的 JSON，对象形式如下：

        {
          "papers": [
            {
              "categories": [...],
              "title": "...",
              "journal": "...",
              "doi": "...",
              "date": "...",
              "study_type": "...",
              "summary": "...",
              "key_conclusions": "...",
              "limitations": "...",
              "disease": "...",
              "aim": "...",

              "task_type": "...",
              "bio_relevance": "...",
              "metrics": "...",
              "architecture": "...",
              "data_source": "...",
              "code_hardware": "...",

              "species_model": "...",
              "sample_size": "...",
              "key_techniques": ["...", "..."],
              "target_pathway": "...",
              "validation": "...",

              "omics_data_type": "...",
              "sample_details": "...",
              "cell_types": "...",
              "analysis_workflow": "...",
              "innovative_methods": "...",
              "reproducibility": "..."
            }
          ]
        }

        要求：
        - 所有字段都必须出现，缺失信息用 "N/A"
        - 不要额外增加本 Schema 未定义的字段
        - 不要在 JSON 外包裹额外文字
        """
    )
    return prompt


def call_llm(client: OpenAI, pdf_text: str) -> dict:
    debug("调用 LLM 进行结构化抽取...")
    system_prompt = build_system_prompt()
    user_prompt = "文献内容：\n" + pdf_text[:20000]

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        debug("✅ LLM 返回 JSON 解析成功")
        return data
    except Exception as e:
        debug(f"❌ LLM 调用或解析失败: {e}")
        if "content" in locals():
            debug(f"原始返回内容: {content}")
        return {"papers": []}


def json_to_python_code(papers_list):
    code = "papers = " + json.dumps(papers_list, ensure_ascii=False, indent=4)
    return code


def main():
    debug("=== batch_run.py 启动 ===")

    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        debug("⚠ 未设置 OPENAI_API_KEY，请先在 .env 中配置。")
        return

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )

    try:
        zot = get_zotero_client()
        items = fetch_items_from_collection(zot)
    except Exception:
        traceback.print_exc()
        return

    all_papers = []

    for idx, item in enumerate(items, start=1):
        title = item["data"].get("title", "无标题")
        debug(f"--- 处理第 {idx} 篇：{title} ---")

        attachment = get_pdf_attachment(zot, item)
        if not attachment:
            debug("跳过：无 PDF 附件")
            continue

        try:
            pdf_path = download_pdf(zot, attachment)
            pdf_text = extract_pdf_text(pdf_path)
        except Exception:
            debug(f"❌ 处理 PDF 失败，跳过: {title}")
            continue

        if not pdf_text.strip():
            debug("⚠ 文本为空，跳过")
            continue

        data = call_llm(client, pdf_text)
        papers = data.get("papers", [])

        if papers:
            for p in papers:
                if p.get("doi") == "N/A":
                    p["doi"] = item["data"].get("DOI", "N/A")
                if p.get("title") == "N/A":
                    p["title"] = title
            all_papers.extend(papers)
        else:
            debug("⚠ LLM 未返回有效 papers 数据")

    if not all_papers:
        debug("⚠ 未生成任何数据，结束。")
        return

    code_str = json_to_python_code(all_papers)
    output_path = Path(OUTPUT_PY_PATH)
    output_path.write_text(code_str, encoding="utf-8")

    debug(f"🎉 成功！已生成文件：{output_path}")
    debug(f"现在请打开 {output_path}，全选复制内容，粘贴到 papers_to_add_example.py 或 papers_to_add.py")


if __name__ == "__main__":
    main()
