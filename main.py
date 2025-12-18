import arxiv
import google.generativeai as genai
import json
from datetime import datetime
import os

# 1. 直接在这里填入你新申请的 API Key
# 确认该 Key 在 AI Studio (aistudio.google.com) 测试可用
MY_API_KEY = "这里填入你的新Key"


def get_ai_summary(title, abstract):
    """调用 Gemini 生成中文总结，带失败重试逻辑"""
    genai.configure(api_key=MY_API_KEY)

    # 尝试多个可能的模型 ID 路径
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro']

    prompt = f"请作为AI专家，用中文简要总结论文的核心贡献：标题：{title}，摘要：{abstract}"

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            continue
    return f"总结失败。报错信息: {last_error}"


def fetch_papers():
    print("开始抓取论文...")
    search = arxiv.Search(
        query="cat:cs.AI OR cat:cs.LG",
        max_results=3,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers_data = []
    for result in search.results():
        print(f"处理中: {result.title[:30]}")
        papers_data.append({
            "title": result.title,
            "link": result.pdf_url,
            "ai_summary": get_ai_summary(result.title, result.summary),
            "date": str(result.published.date())
        })

    output = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "papers": papers_data
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("✨ data.json 更新成功！")


if __name__ == "__main__":
    fetch_papers()