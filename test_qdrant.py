import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
print(f"QDRANT_URL from os: {os.getenv('QDRANT_URL')}")

from backend.kshiraj.knowledge.vector_store import VectorStore
v = VectorStore(dimension=3072)
print(f"VectorStore url: {v._url}")

try:
    client = v._get_client()
    print(f"Client collections: {client.get_collections()}")
except Exception as e:
    print(f"Error: {e}")

