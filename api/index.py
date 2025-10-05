from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from pathlib import Path
import json

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the dataset once when the app starts
DATA_FILE = Path(__file__).parent / "q-vercel-latency.json"
with open(DATA_FILE) as f:
    data = json.load(f)
df = pd.DataFrame(data)

@app.get("/")
async def root():
    return {"message": "Vercel Latency Analytics API is running."}

# CHANGED: This is the key fix - changed from "/api/" to "/api/latency"
@app.post("/api/latency")
async def get_latency_stats(payload: dict):
    regions_to_process = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)
    
    results = {}
    
    for region in regions_to_process:
        region_df = df[df["region"] == region]
        
        if not region_df.empty:
            # Calculate mean latency
            avg_latency = round(region_df["latency_ms"].mean(), 2)
            
            # Calculate 95th percentile latency
            p95_latency = round(np.percentile(region_df["latency_ms"], 95), 2)
            
            # Calculate mean uptime
            avg_uptime = round(region_df["uptime_pct"].mean(), 3)
            
            # Count breaches (records above threshold)
            breaches = int(region_df[region_df["latency_ms"] > threshold].shape[0])
            
            results[region] = {
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches,
            }
    
    return results
