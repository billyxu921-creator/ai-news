import arxiv
import google.generativeai as genai
import json
from datetime import datetime

# 直接在这里填入你新申请的 API Key，不要用变量读取了
API_KEY = "AIzaSyDAYW4cqZ5ZGCmabBFx6BuoPDhQgVP3gOw"

def get_ai_summary(title, abstract):
    genai.configure(api_key=API_KEY)
    # 强制指定 v1beta 版本以确保 1.5-flash 可用
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"请用中文总结这篇论文的核心贡献：标题：{title}，摘要：{abstract}"
    
    try:
        response = model.generate_content(prompt)
        return response.text if response.text else "总结生成失败"
    except Exception as e:
        return f"AI调用报错: {str(e)}"

def run():
    print("开始获取论文...")
    search = arxiv.Search(query="cat:cs.AI", max_results=3, sort_by=arxiv.SortCriterion.SubmittedDate)
    
    results = []
    for p in search.results():
        results.append({
            "title": p.title,
            "link": p.pdf_url,
            "ai_summary": get_ai_summary(p.title, p.summary),
            "date": str(p.published.date())
        })
    
    data = {"update_time": datetime.now().strftime("%Y-%m-%d"), "papers": results}
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("更新完成！")

if __name__ == "__main__":
    run()
