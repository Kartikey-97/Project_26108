from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.recommender import Recommender

app = FastAPI(title="Indian Standards Recommendation Engine")

# Initialize recommender globally
try:
    recommender = Recommender()
except Exception as e:
    recommender = None
    print(f"Failed to initialize recommender: {e}")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

@app.get("/")
def root():
    return {"message": "Welcome to the Indian Standards Recommendation Engine API"}

@app.post("/recommend")
def recommend(request: QueryRequest):
    if not recommender:
        raise HTTPException(status_code=500, detail="Recommender model not loaded.")
        
    results = recommender.recommend(request.query, top_k=request.top_k)
    return {"query": request.query, "recommendations": results}
