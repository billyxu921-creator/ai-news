import arxiv
import json
import os
from datetime import datetime
from google import genai  # 使用最新的 Google GenAI SDK

# ==========================================
# 配置部分
# ==========================================

# 从 GitHub Actions 的 Secrets 中安全读取 Key
# 请确保你在 GitHub 仓库设置里添加了名为 GEMINI_API_KEY 的 Secret
API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_summary(title, abstract):
    """调用 Gemini 2.0 Flash 生成论文中文总结"""
    if not API_KEY:
        return "错误：未检测到 API_KEY。请在 GitHub Secrets 中配置。"

    # 初始化客户端
    client = genai.Client(api_key=API_KEY)

    # 构造提示词
    prompt = f"""你是一名顶尖的 AI 研究员。请用中文简明扼要地总结以下论文：
    1. 核心目标是什么？
    2. 采用了什么关键技术？
    3. 有什么创新亮点？

    标题：{title}
    摘要：{abstract}
    """

    try:
        # 使用最新的 Gemini 2.0 Flash 模型
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        if response and response.text:
            return response.text.strip()
        else:
            return "AI 未返回有效内容"

    except Exception as e:
        # 捕捉泄露报错或其他异常
        return f"总结失败。报错信息: {str(e)}"

def run_task():
    print(f"[{datetime.now()}] 🚀 开始执行抓取任务...")

    # 搜索 arXiv 上的 AI 相关论文
    search = arxiv.Search(
        query="cat:cs.AI OR cat:cs.LG",
        max_results=3,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers_data = []

    for result in search.results():
        print(f"正在分析论文: {result.title[:50]}...")

        summary = get_ai_summary(result.title, result.summary)

        papers_data.append({
            "title": result.title,
            "link": result.pdf_url,
            "ai_summary": summary,
            "date": str(result.published.date())
        })

    # 构建输出 JSON
    output = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "papers": papers_data
    }

    # 保存到文件
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"[{datetime.now()}] ✅ data.json 已成功更新！")

if __name__ == "__main__":
    run_task()