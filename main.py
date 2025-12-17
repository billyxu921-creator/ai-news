import arxiv
import google.generativeai as genai
import json
from datetime import datetime
import os

# 1. 配置 Gemini (适配本地和 GitHub Actions)
# 逻辑：优先读取 GitHub 的“保险柜”(Secret)，如果没有则使用你提供的 Key 跑本地
api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyDQIjW5d7bcCFPuwKaBeH_9l_zHjbvmVV4"

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')


def get_ai_summary(title, abstract):
    """调用 Gemini 生成中文总结"""
    prompt = f"""
    请作为AI领域专家，用中文分析这篇论文并输出：
    1. Summary（一句话概括论文目的）
    2. Methods（核心方法）
    3. 核心创新点（请用3个简短的列表符号展示）

    论文标题: {title}
    摘要: {abstract}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini 调用出错: {e}")
        return "总结生成失败，请查看原文。"


def fetch_papers():
    """从 arXiv 抓取最新 AI 论文并保存"""
    # 搜索最新的 AI 论文 (cs.AI = 人工智能, cs.LG = 机器学习)
    search = arxiv.Search(
        query="cat:cs.AI OR cat:cs.LG",
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers_data = []
    print("正在搬运论文并请求 Gemini 总结，请稍候...")

    for result in search.results():
        summary_text = get_ai_summary(result.title, result.summary)
        # 这里的键名 (Key) 必须和 index.html 里的 JavaScript 对应
        papers_data.append({
            "title": result.title,
            "link": result.pdf_url,
            "authors": ", ".join(author.name for author in result.authors[:3]),
            "ai_summary": summary_text,
            "category": "Artificial Intelligence",
            "id": result.entry_id.split('/')[-1],
            "date": str(result.published.date())
        })

    # 封装最终 JSON 格式
    output = {
        "update_time": str(datetime.now().strftime("%Y-%m-%d %H:%M")),
        "papers": papers_data
    }

    # 写入文件
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("✨ 数据更新成功！生成了 data.json")


if __name__ == "__main__":
    fetch_papers()