from pydantic import BaseModel
from typing import Optional, List, Any

class AnalysisRequest(BaseModel):
    patient_id: str
    data_type: str  # 'tabular', 'image', 'text'
    # For tabular data
    parameters: Optional[dict] = None

class AnalysisResponse(BaseModel):
    diagnosis: str
    confidence: float
    details: dict
    visual_output_path: Optional[str] = None
