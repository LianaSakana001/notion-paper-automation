# notion_utils.py
import os
import logging
from notion_client import Client
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

# 简单的日期清洗工具
def ensure_iso_date(date_str):
    if not date_str:
        return None
    # 把 2025/12/08 这类替换成 2025-12-08
    return date_str.replace("/", "-")


# 读取 .env 文件
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if NOTION_TOKEN is None or NOTION_DATABASE_ID is None:
    raise ValueError("请先在 .env 中配置 NOTION_TOKEN 和 NOTION_DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)


# ======================
# 公共字段（适用于三类文献）
# ======================
def build_common_properties(paper: dict):
    # 修复点：从 paper 字典里获取 categories，而不是读取不存在的变量
    categories = paper.get("categories", [])

    props = {
        "标题 (Title)": {
            "title": [{"text": {"content": paper.get("title", "Untitled")}}]
        },
        "期刊 (Journal)": {
            "rich_text": [{"text": {"content": paper.get("journal", "")}}]
        },
        "DOI": {
            "rich_text": [{
                "text": {
                    "content": paper.get("doi", ""),
                    "link": {"url": f"https://doi.org/{paper.get('doi', '')}"}
                }
            }]
        },
        "一句话总结 (Summary)": {
            "rich_text": [{"text": {"content": paper.get("summary", "")}}]
        },
        "关键结论 (Key Conclusions)": {
            "rich_text": [{"text": {"content": paper.get("key_conclusions", "")}}]
        },
        "局限性与未来方向 (Limitations & Future)": {
            "rich_text": [{"text": {"content": paper.get("limitations", "")}}]
        },
        "研究类型 (Study Type)": {
            "select": {"name": paper.get("study_type", "")}
        } if paper.get("study_type") else None,
    
        # 修复点：使用上面获取的 local 变量 categories
        "文献类别 (Category)": {
            "multi_select": [{"name": c} for c in categories]
        } if categories else None,
        "研究疾病 (Disease)": {
            "rich_text": [{"text": {"content": paper.get("disease", "")}}]
        },
        "研究目的 (Research Aim)": {
            "rich_text": [{"text": {"content": paper.get("aim", "")}}]
        },
    }

    # 发表时间
    pub_date = ensure_iso_date(paper.get("date"))
    if pub_date:
        props["发表时间 (Date)"] = {"date": {"start": pub_date}}

    # 去掉 None 的项，防止 Notion 报错
    return {k: v for k, v in props.items() if v is not None}


# ======================
# 表 1：AI + 生物医学（算法类）
# ======================
def build_ai_bio_properties(paper: dict):
    props = {
        "任务类型 (Task Type)": {
            "rich_text": [{"text": {"content": paper.get("task_type", "")}}]
        } if paper.get("task_type") else None,
        "生物/临床意义 (Clinical/Bio Relevance)": {
            "rich_text": [{"text": {"content": paper.get("bio_relevance", "")}}]
        },
        "评价指标 (Evaluation Metrics)": {
            "rich_text": [{"text": {"content": paper.get("metrics", "")}}]
        },
        "算法/模型架构 (Algorithm/Architecture)": {
            "rich_text": [{"text": {"content": paper.get("architecture", "")}}]
        },
        "数据来源与获取 (Data Source)": {
            "rich_text": [{"text": {"content": paper.get("data_source", "")}}]
        },
        "代码/算力要求 (Code & Hardware)": {
            "rich_text": [{"text": {"content": paper.get("code_hardware", "")}}]
        },
    }
    return {k: v for k, v in props.items() if v is not None}


# ======================
# 表 2：生物医学 / 机制研究（Wet Lab）
# ======================
def build_wetlab_properties(paper: dict):
    # 处理 key_techniques：既兼容 list，也兼容 str
    raw_k = paper.get("key_techniques")

    if isinstance(raw_k, list):
        key_techniques_str = ", ".join(raw_k)
    elif isinstance(raw_k, str):
        key_techniques_str = raw_k
    else:
        key_techniques_str = ""

    props = {
        "物种与模型 (Species & Model)": {
            "rich_text": [{"text": {"content": paper.get("species_model", "")}}]
        },
        "样本量统计 (Sample Size)": {
            "rich_text": [{"text": {"content": paper.get("sample_size", "")}}]
        },
        "关键技术 (Key Techniques)": {
            "rich_text": [{
                "text": {
                    "content": key_techniques_str
                }
            }]
        } if key_techniques_str else None,
        "核心通路/分子 (Target Pathway)": {
            "rich_text": [{"text": {"content": paper.get("target_pathway", "")}}]
        },
        "验证试验 (Validation)": {
            "rich_text": [{"text": {"content": paper.get("validation", "")}}]
        },
    }
    return {k: v for k, v in props.items() if v is not None}


# ======================
# 表 3：组学 / 图谱 / 多组学
# ======================
def build_omics_properties(paper: dict):
    # 兼容两种命名：omics_data_type（新规范） / data_types（旧规范）
    raw_data_type = paper.get("omics_data_type") or paper.get("data_types")

    if isinstance(raw_data_type, list):
        data_type_str = ", ".join(raw_data_type)
    elif isinstance(raw_data_type, str):
        data_type_str = raw_data_type
    else:
        data_type_str = ""

    # 兼容 analysis_workflow（新） 和 workflow（旧）
    workflow_str = paper.get("analysis_workflow") or paper.get("workflow", "")

    props = {
        "数据类型 (Data Type)": {
            "rich_text": [{"text": {"content": data_type_str}}]
        } if data_type_str else None,
        "样本详情 (Sample Details)": {
            "rich_text": [{"text": {"content": paper.get("sample_details", "")}}]
        },
        "细胞类型/分群 (Cell Types)": {
            "rich_text": [{"text": {"content": paper.get("cell_types", "")}}]
        },
        "分析思路 (Analytical Workflow)": {
            "rich_text": [{"text": {"content": workflow_str}}]
        },
        "创新分析方法 (Innovative Methods)": {
            "rich_text": [{"text": {"content": paper.get("innovative_methods", "")}}]
        },
        "可重复性信息 (Reproducibility)": {
            "rich_text": [{"text": {"content": paper.get("reproducibility", "")}}]
        },
    }
    return {k: v for k, v in props.items() if v is not None}


# ======================
# 主函数：根据 category 合并字段并写入 Notion
# ======================
def add_paper_to_notion(paper: dict):
    """
    paper 可以包含：
      - "categories": ["AI + 生物医学 (算法类)", "组学/图谱/多组学"]
      - 或旧格式: "category": "AI + 生物医学 (算法类)"

    合法类别：
      技术类：
        - "AI + 生物医学 (算法类)"
        - "生物医学/机制研究 (Wet Lab)" 或 "生物学 / 机制研究 (Wet Lab)"
        - "组学/图谱/多组学" 或 "组学 / 图谱 / 多组学"
      特殊类：
        - "综述"
        - "其他"

    逻辑：
      - 若包含“综述”或“其他” → 只写公共字段。
      - 否则：
          有 AI → 填 AI 专属字段
          有 Wet Lab → 填 Wet Lab 字段
          有 组学 → 填组学字段
          （可以任意组合）
    """
    title = paper.get("title", "Unknown Title")

    raw_categories = paper.get("categories") or paper.get("category")

    if isinstance(raw_categories, str):
        category_list = [raw_categories] if raw_categories else []
    elif isinstance(raw_categories, list):
        category_list = [c for c in raw_categories if c]
    else:
        category_list = []

    if not category_list:
        raise ValueError(f"文献数据缺少 'category/categories' 字段: {title}")

    # 第一版标准技术类名称
    STD_AI = "AI + 生物医学 (算法类)"
    STD_WETLAB = "生物医学/机制研究 (Wet Lab)"
    STD_OMICS = "组学/图谱/多组学"

    # 特殊类：综述、其他
    TYPE_REVIEW = "综述"
    TYPE_OTHER = "其他"

    CATEGORY_MAP = {
        # AI 类
        "AI + 生物医学 (算法类)": STD_AI,

        # Wet Lab：新旧写法统一
        "生物医学/机制研究 (Wet Lab)": STD_WETLAB,
        "生物学 / 机制研究 (Wet Lab)": STD_WETLAB,

        # 组学：新旧写法统一
        "组学/图谱/多组学": STD_OMICS,
        "组学 / 图谱 / 多组学": STD_OMICS,

        # 特殊类
        "综述": TYPE_REVIEW,
        "其他": TYPE_OTHER,
    }

    std_categories = []
    for c in category_list:
        mapped = CATEGORY_MAP.get(c)
        if not mapped:
            raise ValueError(f"未知 category: {c}")
        std_categories.append(mapped)

    # 为后续使用，存回 paper（供 build_common_properties 用）
    paper["categories"] = std_categories

    # ==== 判定是否为综述/其他 ====
    if TYPE_REVIEW in std_categories or TYPE_OTHER in std_categories:
        # 综述 & 其他：只写公共字段
        try:
            properties = build_common_properties(paper)
        except Exception as e:
            print(f"❌ [数据构建阶段出错] 标题: {title}")
            raise e

    else:
        # ==== 原创研究：根据类别组合填对应字段 ====
        try:
            properties = build_common_properties(paper)

            if STD_AI in std_categories:
                properties.update(build_ai_bio_properties(paper))
            if STD_WETLAB in std_categories:
                properties.update(build_wetlab_properties(paper))
            if STD_OMICS in std_categories:
                properties.update(build_omics_properties(paper))

        except Exception as e:
            print(f"❌ [数据构建阶段出错] 标题: {title}")
            raise e

    # 下面 Notion API 写入部分不变
    try:
        logging.info(f"➡ 正在写入 Notion：{title}")
        res = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=properties
        )
        print(f"✅ 成功写入 Notion: {title}")
        return res

    except Exception as e:
        print(f"❌ [Notion API 请求出错] 标题: {title}")
        print(f"   错误详情: {e}")
        raise e
