---
title: Finsight
emoji: 📊
colorFrom: green
colorTo: black
sdk: docker
app_port: 7860
pinned: false
---

# FinSight 📊

> AI-powered financial research assistant that generates institutional-quality research reports in seconds.

**Live Demo:** https://finsight-zawm.onrender.com/ui

---

## What it does

FinSight takes a company name and automatically generates a structured financial research report by:

- Fetching the latest 10-K annual filing directly from SEC EDGAR
- Searching recent news via Tavily
- Extracting verified financial metrics (revenue, margins, EPS) from EDGAR's structured data API
- Analyzing risk factors from the actual filing
- Compiling everything into a professional research report

What takes a junior analyst 4-6 hours takes FinSight under 60 seconds.

---

## Architecture
User input (company name)
↓
Orchestrator agent
↓
┌───────────────────────────────────┐
│ News Agent │ RAG Agent │
│ (Tavily) │ (SEC 10-K) │
├───────────────────────────────────┤
│ Calculator │ Risk Agent │
│ (EDGAR API) │ (SEC 10-K) │
└───────────────────────────────────┘
↓
Report Writer Agent
↓
Structured research report
---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq (Llama 3.3 70B) |
| Web search | Tavily API |
| Financial data | SEC EDGAR API (free) |
| Document retrieval | RAG with keyword search |
| Backend | FastAPI |
| Frontend | Bloomberg-style HTML/CSS/JS terminal |
| Deployment | Render |

---

## Project Structure
finsight/
├── agents/
│ ├── news_agent.py # Tavily news search + summarization
│ ├── rag_agent.py # SEC filing retrieval + Q&A
│ ├── risk_agent.py # Risk factor extraction
│ ├── report_writer.py # Compiles final report
│ └── orchestrator.py # Coordinates all agents
├── utils/
│ └── sec_fetcher.py # SEC EDGAR API integration
├── templates/
│ └── index.html # Bloomberg terminal UI
├── app.py # FastAPI backend
├── requirements.txt
└── Dockerfile
---

## Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/your-username/finsight.git
cd finsight
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add API keys**

Create a `.env` file:
GROQ_API_KEY=your-groq-key
TAVILY_API_KEY=your-tavily-key
**5. Run**
```bash
uvicorn app:app --reload
```

Open http://localhost:8000/ui

---

## Sample Output

FinSight generates reports with these sections:

- **Company Overview** — what the company does, from their actual SEC filing
- **Recent News** — summarized from latest news articles
- **Financial Performance** — verified revenue, margins, EPS from EDGAR
- **Key Risk Factors** — extracted from the 10-K risk section
- **Investment Thesis** — synthesized view from all the above

---

## Disclaimer

⚠️ This tool is for informational purposes only and does not constitute financial or investment advice. Always consult a qualified financial advisor before making investment decisions. Data sourced from SEC EDGAR and public news sources.

---

## Built with

- [Groq](https://groq.com) — LLM inference
- [Tavily](https://tavily.com) — News search API  
- [SEC EDGAR](https://www.sec.gov/edgar) — Financial filings
- [FastAPI](https://fastapi.tiangolo.com) — Backend framework
- [LangChain](https://langchain.com) — Document processing