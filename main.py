# main.py
"""
主入口：读取 papers_to_add_example.py 中的 papers 列表，
通过 notion_utils.add_paper_to_notion 写入 Notion 数据库。

使用方法：
    1. 编辑 papers_to_add_example.py（或你自己的 papers_to_add.py）
    2. 运行：python main.py
"""

from notion_utils import add_paper_to_notion

try:
    # 你也可以改成 from papers_to_add import papers
    from papers_to_add_example import papers
except ImportError:
    raise ImportError(
        "未找到 papers_to_add_example.papers，请确认文件存在且包含 papers = [...]"
    )


def main():
    success_count = 0
    fail_count = 0

    for paper in papers:
        title = paper.get("title", "Untitled")
        try:
            add_paper_to_notion(paper)
            success_count += 1
        except Exception as e:
            fail_count += 1
            print(f"❌ [写入失败] 标题: {title}")
            print(f"   错误详情: {e}")

    print(f"\n✅ 写入完成：成功 {success_count} 篇，失败 {fail_count} 篇。")


if __name__ == "__main__":
    main()
