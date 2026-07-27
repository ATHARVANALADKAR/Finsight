import os
from groq import Groq
from agents.rag_agent import rag_agent

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def risk_agent(company: str) -> str:
    """Extract and analyze key risk factors from the SEC filing"""
    print(f"⚠️ Risk Agent analyzing {company} risks...")

    risk_context = rag_agent(
        "risk factors business risks competition regulatory legal cybersecurity",
        company
    )

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": f"""You are a risk analyst reviewing {company}'s SEC filing.
Extract the top 5 most significant risk factors.
For each risk provide:
- Risk name (short)
- Brief explanation (1-2 sentences)  
- Impact level: High / Medium / Low

Format as:
RISK 1: [name]
Description: [explanation]
Impact: [level]"""
            },
            {
                "role": "user",
                "content": f"Risk information from {company} 10-K:\n{risk_context}"
            }
        ]
    )

    result = response.choices[0].message.content
    print("✅ Risk Agent done!")
    return result