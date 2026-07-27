import requests
from datetime import date

HEADERS = {"User-Agent": "FinSight research@finsight.com"}

def get_company_cik(company_name: str) -> tuple[str, str]:
    """Look up a company's CIK and full name from SEC EDGAR"""
    url = f"https://efts.sec.gov/LATEST/search-index?q=%22{company_name}%22&forms=10-K"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return None, None
    
    hits = response.json().get("hits", {}).get("hits", [])
    if not hits:
        return None, None
    
    source = hits[0]["_source"]
    ciks = source.get("ciks", [])
    names = source.get("display_names", [company_name])
    
    if not ciks:
        return None, None
    
    return ciks[0].zfill(10), names[0] if names else company_name


def get_sec_filing(company_name: str) -> dict | None:
    """Get the most recent 10-K filing metadata"""
    url = f"https://efts.sec.gov/LATEST/search-index?q=%22{company_name}%22&dateRange=custom&startdt=2023-01-01&forms=10-K"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return None
    
    hits = response.json().get("hits", {}).get("hits", [])
    return hits[0]["_source"] if hits else None


def get_raw_filing_text(adsh: str, cik: str) -> str | None:
    """Fetch raw text of an SEC filing"""
    import re
    
    cik_clean = str(int(cik))
    adsh_formatted = adsh.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_clean}/{adsh_formatted}/{adsh}.txt"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return None
    
    text = response.text[:100000]
    
    # find start of actual content
    for marker in ["ITEM 1.", "Item 1.", "PART I", "Part I"]:
        idx = text.find(marker)
        if idx != -1:
            text = text[idx:]
            break
    
    return clean_filing_text(text)


def clean_filing_text(text: str) -> str:
    """Clean HTML entities and noise from SEC filing text"""
    import re
    
    replacements = {
        "&nbsp;": " ", "&#160;": " ", "&#8217;": "'",
        "&#8220;": '"', "&#8221;": '"', "&#8212;": "—",
        "&#38;": "&", "&amp;": "&", "&lt;": "<", "&gt;": ">"
    }
    for entity, char in replacements.items():
        text = text.replace(entity, char)
    
    text = re.sub(r'<[^>]+>', ' ', text)
    lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 3]
    text = "\n".join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {3,}', ' ', text)
    
    return text.strip()


def get_financial_metrics(cik: str, company_name: str) -> str:
    """Fetch structured financial data from SEC EDGAR facts API"""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return f"Error fetching financials: {response.status_code}"
    
    facts = response.json().get("facts", {}).get("us-gaap", {})
    
    def get_latest_annual(fact_keys, unit="USD"):
        for key in fact_keys:
            if key not in facts:
                continue
            units = facts[key].get("units", {}).get(unit, [])
            annual = [x for x in units if x.get("form") == "10-K" and x.get("fp") == "FY"]
            for entry in sorted(annual, key=lambda x: x.get("end", ""), reverse=True):
                if "start" in entry and "end" in entry:
                    try:
                        start = date.fromisoformat(entry["start"])
                        end = date.fromisoformat(entry["end"])
                        if 355 <= (end - start).days <= 400:
                            return entry["val"], entry["end"]
                    except:
                        continue
        return None, None

    revenue, rev_date      = get_latest_annual(["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"])
    net_income, _          = get_latest_annual(["NetIncomeLoss"])
    gross_profit, _        = get_latest_annual(["GrossProfit"])
    operating_income, _    = get_latest_annual(["OperatingIncomeLoss"])
    eps, _                 = get_latest_annual(["EarningsPerShareDiluted"], unit="USD/shares")

    def fmt_b(val): return f"${val/1e9:.2f}B" if val else "N/A"
    def fmt_pct(num, den): return f"{num/den*100:.1f}%" if num and den else "N/A"
    def fmt_eps(val): return f"${val:.2f}" if val else "N/A"

    return f"""
{company_name} Financial Metrics (FY ending {rev_date or 'Unknown'})
{'='*50}
Revenue:          {fmt_b(revenue)}
Gross Profit:     {fmt_b(gross_profit)}
Operating Income: {fmt_b(operating_income)}
Net Income:       {fmt_b(net_income)}
EPS (Diluted):    {fmt_eps(eps)}

Key Ratios:
Gross Margin:     {fmt_pct(gross_profit, revenue)}
Operating Margin: {fmt_pct(operating_income, revenue)}
Net Margin:       {fmt_pct(net_income, revenue)}
""".strip()