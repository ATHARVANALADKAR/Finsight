import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from agents.orchestrator import orchestrator

app = FastAPI(title="FinSight API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

class CompanyRequest(BaseModel):
    company: str

@app.get("/")
def home():
    return {"message": "FinSight API running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze(request: CompanyRequest):
    try:
        report = orchestrator(request.company)
        return {"company": request.company, "report": report, "status": "success"}
    except Exception as e:
        return {"company": request.company, "report": str(e), "status": "error"}

@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )