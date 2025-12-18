import arxiv
import json
from datetime import datetime
import requests  # DeepSeek 使用简单的 requests 即可

# 1. 配置 DeepSeek (请填入你的 API Key)
DEEPSEEK_API_KEY = "sk-7a870ec1ad6f4db2bb6b1169f8c8bd37"

def get_ai_summary(title, abstract):
    """调用 DeepSeek 生成中文总结"""
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat", # 或者使用 deepseek-reasoner (R1模型)
        "messages": [
            {"role": "system", "content": "你是一个AI论文专家，请用中文简洁总结论文的核心贡献。"},
            {"role": "user", "content": f"标题: {title}\n摘要: {abstract}"}
        ],
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        res_json = response.json()
        return res_json['choices'][0]['message']['content']
    except Exception as e:
        return f"DeepSeek 调用失败: {str(e)}"

def fetch_papers():
    print("开始从 arXiv 抓取论文...")
    search = arxiv.Search(
        query = "cat:cs.AI OR cat:cs.LG",
        max_results = 5,
        sort_by = arxiv.SortCriterion.SubmittedDate
    )
    
    papers_data = []
    for result in search.results():
        print(f"总结中: {result.title[:30]}...")
        summary_text = get_ai_summary(result.title, result.summary)
        
        papers_data.append({
            "title": result.title,
            "link": result.pdf_url,
            "authors": ", ".join(author.name for author in result.authors[:3]),
            "ai_summary": summary_text,
            "category": "AI & Machine Learning",
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
