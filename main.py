import arxiv
import google.generativeai as genai
import json
from datetime import datetime

# 1. 配置 Gemini
genai.configure(api_key="AIzaSyDQIjW5d7bcCFPuwKaBeH_9l_zHjbvmVV4")
model = genai.GenerativeModel('gemini-1.5-flash')


def get_ai_summary(title, abstract):
    # 构建精准的 Prompt
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
    except:
        return "总结生成失败，请查看原文。"


def fetch_papers():
    # 搜索 arXiv 最新 AI 论文
    search = arxiv.Search(
        query="cat:cs.AI OR cat:cs.LG",
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers_data = []
    print("正在搬运论文并请求 Gemini 总结，请稍候...")

    for result in search.results():
        summary_text = get_ai_summary(result.title, result.summary)
        papers_data.append({
            "title": result.title,
            "link": result.pdf_url,
            "authors": ", ".join(author.name for author in result.authors[:3]),
            "ai_summary": summary_text,  # 👈 检查这里！一定要叫 ai_summary
            "category": "Artificial Intelligence",  # 👈 检查这里！一定要叫 category
            "id": result.entry_id.split('/')[-1]  # 👈 检查这里！一定要叫 id
        })

    # 保存为 JSON 文件供网页读取
    output = {
        "update_time": str(datetime.now().strftime("%Y-%m-%d %H:%M")),
        "papers": papers_data
    }
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("数据更新成功！生成了 data.json")


if __name__ == "__main__":
    fetch_papers()