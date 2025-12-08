# batch_mode/config.py  

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# 读取 .env
load_dotenv()

# ===== Zotero 配置（可选功能） =====
ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY", "")
ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID", "")
ZOTERO_LIBRARY_TYPE = os.getenv("ZOTERO_LIBRARY_TYPE", "user")
ZOTERO_COLLECTION_KEY = os.getenv("ZOTERO_COLLECTION_KEY", "")

# 最多读取多少条文献
MAX_ITEMS = int(os.getenv("MAX_ITEMS", "10"))

# ===== LLM / OpenAI 兼容接口 =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "Qwen/Qwen2.5-72B-Instruct")

# ===== 本地 PDF / 输出 路径（相对路径，安全） =====
LOCAL_PDF_DIR = Path(os.getenv("LOCAL_PDF_DIR", BASE_DIR / "local_pdfs"))
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "20"))

# papers 结果输出到根目录下的 papers_generated.py
OUTPUT_PY_PATH = Path(os.getenv("OUTPUT_PY_PATH", BASE_DIR / "papers_generated.py"))
