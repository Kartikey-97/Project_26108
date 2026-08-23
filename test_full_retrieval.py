import asyncio
from backend.shared.config import settings
from backend.kartikey.orchestration.knowledge_registry import initialize_knowledge_registry
from backend.kshiraj.knowledge.retrieval_service import RetrievalQuery
from backend.shared.models import Requirement

async def main():
    settings.semantic_retrieval_enabled = True
    registry = initialize_knowledge_registry()
    
    req = Requirement(id="test", analysis_id="an1", text="System Wattage: 120W", is_reference=None)
    query_text = req.is_reference if req.is_reference else req.text
    
    query = RetrievalQuery(
        query_text=query_text,
        top_k=3,
        include_evidence=False,
    )
    
    result = registry.retrieval_service.search_standards(query)
    print(f"Candidates found: {len(result.candidates)}")

asyncio.run(main())
