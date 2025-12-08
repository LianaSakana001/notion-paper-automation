"""
papers_to_add_example.py

示例文件：演示如何以正确格式向 Notion 写入文献条目。

用户应将 LLM（ChatGPT / Qwen / DeepSeek）生成的结构化文献信息
替换此文件中的 papers = [...] 并运行：

    python main.py

即可自动写入 Notion 数据库。
"""

papers = [
    {
        # 多类别示例：AI + 组学
        "categories": [
            "AI + 生物医学 (算法类)",
            "组学/图谱/多组学"
        ],

        # 公共字段
        "title": "An Integrated Deep Learning Framework for Multi-Omic Cellular State Prediction",
        "journal": "Science Advances",
        "doi": "10.1234/sciadv.2025.000001",
        "date": "2025-01-01",
        "study_type": "AI 模型开发 + 多组学整合",
        "summary": "本研究提出一个深度学习框架，可同时整合 scRNA-seq 和 ATAC-seq 来预测细胞状态，并在多数据集上验证模型泛化能力。",
        "key_conclusions": "模型可跨平台预测细胞状态；在样本不足的条件下仍有稳健性能；揭示 RNA 与染色质调控之间的非线性关联。",
        "limitations": "真实实验验证有限；需要更多物种扩展以提升泛化性。",
        "disease": "N/A",
        "aim": "开发一个 AI 模型来整合多组学数据并预测细胞状态。",

        # AI 类字段
        "task_type": "细胞状态预测（多模态整合）",
        "bio_relevance": "推动多组学数据的跨平台整合，辅助细胞身份判定。",
        "metrics": "AUC, Accuracy, F1-score",
        "architecture": "Transformer + 多模态注意力机制",
        "data_source": "公开 scRNA-seq / ATAC 数据集合并（如 PBMC datasets）",
        "code_hardware": "PyTorch；NVIDIA GPU (16GB+) 建议使用",

        # 组学字段
        "omics_data_type": "scRNA-seq + scATAC-seq",
        "sample_details": "来自多个公开 PBMC 数据集，共计约 20 万细胞。",
        "cell_types": "T cells, B cells, NK cells, Monocytes 等。",
        "analysis_workflow": "数据预处理 → 模态对齐 → Transformer 训练 → 可解释性分析",
        "innovative_methods": "多模态注意力权重用于解释基因–染色质调控关系。",
        "reproducibility": "代码与模型均在 GitHub 上开源。",

        # Wet Lab 字段（此示例无 Wet Lab，保持 N/A）
        "species_model": "N/A",
        "sample_size": "N/A",
        "key_techniques": "N/A",
        "target_pathway": "N/A",
        "validation": "N/A"
    }
]
