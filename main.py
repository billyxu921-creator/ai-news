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
    请作为AI领域专家，用中文分析这篇论文并输出：
    1. Summary（一句话概括论文目的）
    2. Methods（核心方法）
    3. 核心创新点（请用3个简短的列表符号展示）

    论文标题: {title}
    摘要: {abstract}
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