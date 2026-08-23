import asyncio
from backend.shared.config import settings
from backend.kartikey.orchestration.knowledge_registry import initialize_knowledge_registry
from backend.kshiraj.knowledge.retrieval_service import RetrievalQuery

async def main():
    settings.semantic_retrieval_enabled = True
    
    registry = initialize_knowledge_registry()
    print(f"Retrieval mode: {registry.retrieval_mode}")
    
    # Do vector search directly
    query_vec = registry.retrieval_service.embedding_service.encode_text("System Wattage: 120W")
    hits = registry.retrieval_service.vector_store.search_standards(query_vec, top_k=3)
    
    for h in hits:
        print(f"Hit ID: {h['id']}, Payload: {h['payload'].keys() if h['payload'] else 'NO PAYLOAD'}")

asyncio.run(main())
