import arxiv
import google.generativeai as genai
import json
from datetime import datetime
import os

# 1. 配置 Gemini (自动选择最稳健的模型名称)
def setup_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or len(api_key) < 10:
        api_key = "AIzaSyDAYW4cqZ5ZGCmabBFx6BuoPDhQgVP3gOw"
    
    genai.configure(api_key=api_key)
    
    # 我们先尝试标准名称，并在后面增加 fallback 逻辑
    return genai.GenerativeModel('gemini-1.5-flash')

model = setup_gemini()

def get_ai_summary(title, abstract):
    """调用 Gemini 生成中文总结，带失败重试逻辑"""
    prompt = f"""
    请作为AI领域专家，用中文分析这篇论文：
    1. 【核心目标】：一句话概括。
    2. 【技术路径】：详细说明核心方法。
    3. 【创新亮点】：列出3个深度贡献。
    
    论文标题: {title}
    摘要: {abstract}
    """
    
    # 尝试多个可能的模型 ID
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    
    last_error = ""
    for model_name in models_to_try:
        try:
            current_model = genai.GenerativeModel(model_name)
            response = current_model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            continue # 如果当前模型报 404，尝试列表中的下一个
            
    return f"总结生成失败。最后一次尝试报错: {last_error[:50]}"

def fetch_papers():
    """从 arXiv 抓取最新 AI 论文"""
    print("开始抓取论文...")
    search = arxiv.Search(
        query = "cat:cs.AI OR cat:cs.LG",
        max_results = 5,
        sort_by = arxiv.SortCriterion.SubmittedDate
    )
    
    papers_data = []
    for result in search.results():
        print(f"处理中: {result.title[:30]}")
        summary_text = get_ai_summary(result.title, result.summary)
        
        papers_data.append({
            "title": result.title,
            "link": result.pdf_url,
            "authors": ", ".join(author.name for author in result.authors[:3]),
            "ai_summary": summary_text,
            "category": "Artificial Intelligence",
            "id": result.entry_id.split('/')[-1],
            "date": str(result.published.date())
        })
    
    output = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "papers": papers_data
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("✨ data.json 更新成功！")

if __name__ == "__main__":
    fetch_papers()
    fetch_papers()
