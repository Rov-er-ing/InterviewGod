from fastapi import FastAPI, HTTPException, Query
from mangum import Mangum
from signals.orchestrator import Orchestrator
from utils.storage import Storage
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(title="Signal Detection System API")

# Mangum handler for AWS Lambda
handler = Mangum(app)

class DetectionRequest(BaseModel):
    companies: Optional[List[str]] = None
    threshold: Optional[int] = None

# Resolve the absolute path to config.yaml relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

@app.get("/")
def read_root():
    return {
        "message": "Signal Detection System API is running",
        "config_found": os.path.exists(CONFIG_PATH),
        "env": "vercel" if os.environ.get("VERCEL") else "local"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.api_route("/detect", methods=["GET", "POST"])
def detect_signals(company: Optional[str] = None, limit: Optional[int] = Query(5, ge=1, le=10), request: Optional[DetectionRequest] = None):
    """
    Triggers the detection pipeline with safety limits for Serverless environments.
    """
    try:
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
            
        orchestrator = Orchestrator(config_path=CONFIG_PATH)
        
        # Priority 1: Explicit company name in Query Param
        if company:
            orchestrator.companies = [c for c in orchestrator.companies if c.get("name").lower() == company.lower()]
            if not orchestrator.companies:
                return {"status": "error", "message": f"Company '{company}' not found in watch list."}

        # Priority 2: List of companies in POST body
        elif request and request.companies:
            orchestrator.companies = [c for c in orchestrator.companies if c.get("name") in request.companies]
        
        # Priority 3: Default safety limit (Top N companies) to prevent 10s timeout
        else:
            orchestrator.companies = orchestrator.companies[:limit]

        if request and request.threshold is not None:
            orchestrator.config["score_threshold"] = request.threshold

        orchestrator.run()
        
        # Return signals from today's run
        storage = Storage()
        signals = storage.get_all_signals()
        
        return {
            "status": "success",
            "companies_scanned": [c.get("name") for c in orchestrator.companies],
            "signals_detected": len(signals),
            "data": signals,
            "note": "Bulk scans (>10 companies) should be run locally to avoid cloud timeouts."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals")
def get_signals():
    """
    Retrieves all stored signals.
    """
    try:
        storage = Storage()
        return storage.get_all_signals()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
