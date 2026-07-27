import os
from groq import Groq
from tavily import TavilyClient

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def news_agent(company: str) -> str:
    """Search for recent news about a company and return a summary"""
    print(f"📰 News Agent searching for {company} news...")

    results = tavily_client.search(
        query=f"{company} latest news financial results 2024 2025",
        max_results=5,
        topic="news"
    )

    articles = results.get("results", [])
    if not articles:
        return f"No recent news found for {company}"

    news_text = ""
    for i, article in enumerate(articles):
        news_text += f"\nArticle {i+1}: {article['title']}\n"
        news_text += f"Content: {article.get('content', '')[:300]}\n"

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": f"""You are a financial news analyst summarizing recent news about {company}.
Summarize the key developments in 4-5 bullet points.
Focus on: earnings, products, strategy, market position, leadership.
Only use information from the provided articles."""
            },
            {
                "role": "user",
                "content": f"Recent news about {company}:\n{news_text}"
            }
        ]
    )

    result = response.choices[0].message.content
    print("✅ News Agent done!")
    return result