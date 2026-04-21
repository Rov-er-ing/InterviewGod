from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InterviewGod | Signal Detection</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --bg: #0f172a;
                --card: #1e293b;
                --text: #f8fafc;
                --accent: #818cf8;
            }
            body {
                font-family: 'Inter', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                min-height: 100vh;
                padding: 2rem;
            }
            .container {
                width: 100%;
                max-width: 1000px;
            }
            header {
                text-align: center;
                margin-bottom: 3rem;
            }
            h1 {
                font-size: 3rem;
                font-weight: 800;
                background: linear-gradient(to right, #818cf8, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            }
            .controls {
                background: var(--card);
                padding: 1.5rem;
                border-radius: 1rem;
                display: flex;
                gap: 1rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
            }
            input, button {
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                border: none;
                font-size: 1rem;
            }
            input {
                flex-grow: 1;
                background: #334155;
                color: white;
            }
            button {
                background: var(--primary);
                color: white;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, background 0.2s;
            }
            button:hover {
                background: var(--accent);
                transform: translateY(-2px);
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1.5rem;
            }
            .card {
                background: var(--card);
                padding: 1.5rem;
                border-radius: 1rem;
                border: 1px solid rgba(255,255,255,0.1);
                transition: transform 0.3s;
                position: relative;
                overflow: hidden;
            }
            .card:hover {
                transform: scale(1.02);
            }
            .badge {
                position: absolute;
                top: 1rem;
                right: 1rem;
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.75rem;
                font-weight: bold;
                background: #22c55e;
            }
            .score {
                font-size: 2rem;
                font-weight: 800;
                color: var(--accent);
                margin: 1rem 0;
            }
            .title {
                font-weight: 600;
                margin-bottom: 1rem;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }
            .link {
                color: var(--accent);
                text-decoration: none;
                font-size: 0.875rem;
                font-weight: 500;
            }
            #loading {
                display: none;
                margin: 2rem 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>InterviewGod</h1>
                <p>Real-time Mass Hiring Signal Intelligence</p>
            </header>

            <div class="controls">
                <input type="text" id="company" placeholder="Enter company name (e.g. Meta)">
                <button onclick="scan()">Scan Now</button>
            </div>

            <div id="loading">✨ Detecting signals...</div>
            <div id="results" class="grid"></div>
        </div>

        <script>
            async function scan() {
                const company = document.getElementById('company').value;
                const resultsDiv = document.getElementById('results');
                const loading = document.getElementById('loading');
                
                resultsDiv.innerHTML = '';
                loading.style.display = 'block';
                
                try {
                    const url = company ? `/detect?company=${company}&threshold=0` : '/detect?limit=5&threshold=20';
                    const response = await fetch(url);
                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    
                    if (data.status === 'success' && data.data.length > 0) {
                        data.data.forEach(signal => {
                            const card = document.createElement('div');
                            card.className = 'card';
                            card.innerHTML = `
                                <div class="badge">${signal.confidence}</div>
                                <div class="company">${signal.company_name}</div>
                                <div class="score">${signal.score}%</div>
                                <div class="title">${signal.title}</div>
                                <a href="${signal.url}" target="_blank" class="link">View Source →</a>
                            `;
                            resultsDiv.appendChild(card);
                        });
                    } else {
                        resultsDiv.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">No high-confidence leads found. Try a specific company name or lower threshold.</p>';
                    }
                } catch (e) {
                    loading.style.display = 'none';
                    alert('Scan failed. Please try again.');
                }
            }
            
            // Initial scan
            scan();
        </script>
    </body>
    </html>
    """

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.api_route("/detect", methods=["GET", "POST"])
def detect_signals(
    company: Optional[str] = None, 
    limit: Optional[int] = Query(5, ge=1, le=10), 
    threshold: Optional[int] = Query(None, ge=0, le=100),
    show_noise: bool = Query(False),
    request: Optional[DetectionRequest] = None
):
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

        # Set threshold from query param OR request body
        final_threshold = threshold if threshold is not None else (request.threshold if request else None)
        if final_threshold is not None:
            orchestrator.config["score_threshold"] = final_threshold

        signals, total_fetched = orchestrator.run(show_noise=show_noise)
        
        return {
            "status": "success",
            "companies_scanned": [c.get("name") for c in orchestrator.companies],
            "total_articles_fetched": total_fetched,
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
