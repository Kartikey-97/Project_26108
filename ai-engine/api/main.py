from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.reasoning.analyzer import Analyzer

app = FastAPI(title="Indian Standards Recommendation Engine")

analyzer = Analyzer()

# Mocking the models from the backend contract so FastAPI can validate them
class Requirement(BaseModel):
    id: str
    analysis_id: str
    text: str
    normalized_text: Optional[str] = None
    category: str = "other"
    is_reference: Optional[str] = None
    cited_year: Optional[int] = None
    cited_designation: Optional[str] = None
    location: Optional[str] = None
    page: Optional[int] = None
    extracted_at: Optional[str] = None
    extraction_confidence: Optional[float] = None
    from_corrigendum: bool = False
    corrigendum_number: Optional[int] = None

class Standard(BaseModel):
    id: str
    is_number: str
    title: str
    status: str
    year: Optional[int] = None

class AimlRequest(BaseModel):
    analysis_id: str
    extracted_text: str
    requirements: List[Requirement]
    retrieved_standards: List[Standard]

class AimlFinding(BaseModel):
    finding_id: str
    requirement_id: str
    verdict: str
    reason: str
    recommended_action: Optional[str] = None
    applicable_standard_ids: List[str] = []
    evidence_ids: List[str] = []
    confidence: float

class AimlResponse(BaseModel):
    analysis_id: str
    findings: List[AimlFinding]
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)

@app.get("/")
def root():
    return {"message": "Welcome to the Indian Standards Recommendation Engine API"}

@app.post("/analyze", response_model=AimlResponse)
def analyze(request: AimlRequest):
    try:
        response = analyzer.process(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
