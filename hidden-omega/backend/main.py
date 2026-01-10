from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from agents.router_agent import RouterAgent

app = FastAPI(title="Liver Disease AI Diagnostics API")

# Initialize Router (loads all sub-agents)
router_agent = RouterAgent()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Liver Disease AI Diagnostics System Ready"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze/tabular")
async def analyze_tabular(data: dict):
    # Expecting raw JSON dict
    result = router_agent.route_and_predict(data, data_type="tabular")
    return result

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    result = router_agent.route_and_predict(contents, data_type="image", filename=file.filename)
    return result
