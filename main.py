import arxiv
import json
import os
from datetime import datetime
from google import genai  # 使用最新的 SDK

# 直接填入你的 API Key
MY_API_KEY = "AIzaSyDAYW4cqZ5ZGCmabBFx6BuoPDhQgVP3gOw"

def get_ai_summary(title, abstract):
    # 按照快速入门文档初始化客户端
    client = genai.Client(api_key=MY_API_KEY)

    prompt = f"请作为 AI 专家，用中文总结这篇论文的核心亮点：标题：{title}，摘要：{abstract}"

    try:
        # 使用文档推荐的 gemini-2.0-flash 模型
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"总结失败，报错: {str(e)}"


def run():
    print("开始获取论文...")
    search = arxiv.Search(query="cat:cs.AI", max_results=3, sort_by=arxiv.SortCriterion.SubmittedDate)

    results = []
    for p in search.results():
        print(f"正在总结: {p.title[:30]}...")
        results.append({
            "title": p.title,
            "link": p.pdf_url,
            "ai_summary": get_ai_summary(p.title, p.summary),
            "date": str(p.published.date())
        })

    data = {"update_time": datetime.now().strftime("%Y-%m-%d %H:%M"), "papers": results}
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("更新完成！")


if __name__ == "__main__":
    run()