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
def detect_signals(request: Optional[DetectionRequest] = None):
    """
    Triggers the detection pipeline.
    """
    try:
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
            
        orchestrator = Orchestrator(config_path=CONFIG_PATH)
        
        if request:
            if request.companies:
                # Filter companies to only those requested
                # Note: This assumes orchestrator.companies is a list of dicts from companies.json
                all_companies = orchestrator.companies
                orchestrator.companies = [c for c in all_companies if c.get("name") in request.companies]
            
            if request.threshold is not None:
                orchestrator.config["score_threshold"] = request.threshold

        orchestrator.run()
        
        # Return signals from today's run (from the storage)
        storage = Storage()
        signals = storage.get_all_signals()
        
        return {
            "status": "success",
            "signals_detected": len(signals),
            "data": signals
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
