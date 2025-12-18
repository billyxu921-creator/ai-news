import arxiv
import google.generativeai as genai
import json
from datetime import datetime
import os


# 1. 配置 Gemini (增强型适配逻辑)
def setup_gemini():
    # 尝试从 GitHub Secrets 读取
    api_key = os.getenv("GEMINI_API_KEY")

    # 如果环境变量不存在、为空、或者长度明显不对，则使用备用硬编码 Key
    if not api_key or len(api_key) < 10:
        api_key = "AIzaSyDQIjW5d7bcCFPuwKaBeH_9l_zHjbvmVV4"

    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')


model = setup_gemini()


def get_ai_summary(title, abstract):
    """调用 Gemini 生成中文总结"""
    prompt = f"""
    你现在是一名顶尖的 AI 科学家。请深度分析以下论文标题和摘要，并用中文提供高质量总结。
    
    要求：
    1. 【核心目标】：用一句话精准描述该研究解决了什么痛点，不要翻译，要解读。
    2. 【技术路径】：详细说明其使用了什么模型、算法或数学方法（如：Transformer, Diffusions, LoRA等）。
    3. 【创新亮点】：列出该论文最显著的3个贡献，必须具有学术深度。
    
    待处理论文：
    标题: {title}
    摘要: {abstract}
    
    请直接输出内容，不要包含任何多余的开场白
    """
    try:
        response = model.generate_content(prompt)
        # 确保返回的是文本内容
        if response and response.text:
            return response.text
        return "Gemini 返回内容为空，请检查 API 状态。"
    except Exception as e:
        print(f"Gemini 调用出错: {e}")
        return f"总结生成失败。错误信息: {str(e)[:50]}"


def fetch_papers():
    """从 arXiv 抓取最新 AI 论文并保存"""
    print("开始抓取 arXiv 论文...")
    search = arxiv.Search(
        query="cat:cs.AI OR cat:cs.LG",
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers_data = []

    for result in search.results():
        print(f"正在处理: {result.title[:30]}...")
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

    # 封装最终 JSON 格式 (确保与 index.html 的字段匹配)
    output = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "last_updated": datetime.now().strftime("%Y-%m-%d"),  # 兼容你 HTML 里的旧字段
        "papers": papers_data
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("✨ data.json 更新成功！")


if __name__ == "__main__":
    fetch_papers()
