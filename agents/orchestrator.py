import os
from dotenv import load_dotenv

load_dotenv()

from utils.sec_fetcher import (
    get_company_cik,
    get_sec_filing,
    get_raw_filing_text,
    get_financial_metrics
)
from agents.rag_agent import build_rag_pipeline, rag_agent
from agents.news_agent import news_agent
from agents.risk_agent import risk_agent
from agents.report_writer import report_writer


def orchestrator(company_name: str) -> str:
    """
    Main orchestrator — coordinates all specialist agents
    and compiles the final FinSight research report
    """
    print(f"\n{'='*60}")
    print(f"🎯 FinSight — Analyzing {company_name}")
    print(f"{'='*60}")

    # step 1 — look up company
    print("\n🔍 Looking up company on SEC EDGAR...")
    cik, full_name = get_company_cik(company_name)

    if not cik:
        return f"Could not find '{company_name}' on SEC EDGAR. Try the full legal name."

    print(f"Found: {full_name} (CIK: {cik})")

    # step 2 — fetch SEC filing
    print("\n📥 Fetching SEC 10-K filing...")
    filing_data = get_sec_filing(company_name)
    
    filing_loaded = False
    if filing_data and isinstance(filing_data, dict):
        adsh = filing_data.get("adsh")
        if adsh:
            filing_text = get_raw_filing_text(adsh, cik)
            if filing_text:
                filing_loaded = build_rag_pipeline(filing_text, full_name)

    if not filing_loaded:
        print("⚠️ Could not load SEC filing — RAG agent will be limited")

    # step 3 — run all specialist agents
    print("\n🚀 Running specialist agents...")

    overview  = rag_agent(
        f"What does {full_name} do? What are their main products and services?",
        full_name
    ) if filing_loaded else f"SEC filing not available for {full_name}"

    news      = news_agent(full_name)
    financials = get_financial_metrics(cik, full_name)
    risks     = risk_agent(full_name) if filing_loaded else "Risk analysis requires SEC filing"

    # step 4 — compile report
    print("\n📊 Compiling final report...")
    report = report_writer(full_name, overview, news, financials, risks)

    print(f"\n{'='*60}")
    print("✅ FinSight analysis complete!")
    print(f"{'='*60}\n")

    return report


if __name__ == "__main__":
    company = input("Enter company name: ")
    report = orchestrator(company)
    print(report)
    