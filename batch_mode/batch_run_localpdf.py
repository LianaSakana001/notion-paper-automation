# batch_mode/batch_run_localpdf.py

"""
从本地文件夹批量读取 PDF，调用 LLM 抽取文献信息，
生成 papers_generated.py，供用户复制到 papers_to_add_example.py 中。
"""

import traceback
from pathlib import Path

import fitz  # PyMuPDF
from openai import OpenAI

from .config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    LOCAL_PDF_DIR,
    MAX_PDF_PAGES,
    OUTPUT_PY_PATH,
)
from .batch_run import build_system_prompt, call_llm, json_to_python_code, debug


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


def main():
    debug("=== batch_run_localpdf.py 启动 ===")

    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        debug("⚠ 未设置 OPENAI_API_KEY，请先在 .env 中配置。")
        return

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )

    pdf_dir = Path(LOCAL_PDF_DIR)
    if not pdf_dir.exists():
        debug(f"⚠ 本地 PDF 目录不存在：{pdf_dir}，请创建并放入一些 .pdf 文件。")
        return

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        debug(f"⚠ 在目录 {pdf_dir} 中未找到任何 .pdf 文件。")
        return

    all_papers = []

    for idx, pdf_path in enumerate(pdf_files, start=1):
        debug(f"--- 处理第 {idx} 个 PDF：{pdf_path.name} ---")
        try:
            pdf_text = extract_pdf_text(pdf_path)
        except Exception:
            debug(f"❌ PDF 打开或读取失败，跳过：{pdf_path}")
            traceback.print_exc()
            continue

        if not pdf_text.strip():
            debug("⚠ 文本为空，跳过")
            continue

        data = call_llm(client, pdf_text)
        papers = data.get("papers", [])
        if papers:
            # 本地 PDF 没有 Zotero 元数据，这里不做 DOI/标题纠正
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
