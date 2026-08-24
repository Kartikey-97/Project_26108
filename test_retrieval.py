import asyncio
from backend.shared.config import settings
from backend.kartikey.orchestration.knowledge_registry import initialize_knowledge_registry
from backend.kshiraj.knowledge.retrieval_service import RetrievalQuery

async def main():
    # Force semantic retrieval on
    settings.semantic_retrieval_enabled = True
    
    registry = initialize_knowledge_registry()
    print(f"Retrieval mode: {registry.retrieval_mode}")
    
    query = RetrievalQuery(query_text="System Wattage: 120W", top_k=3)
    result = registry.retrieval_service.search_standards(query)
    
    print(f"Candidates found: {len(result.candidates)}")
    for c in result.candidates:
        print(f"- {c.standard.is_number} : {c.score}")

asyncio.run(main())
