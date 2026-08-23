import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        
    def add_embeddings(self, embeddings):
        """Add numpy array of embeddings to the FAISS index."""
        embeddings_np = np.array(embeddings).astype('float32')
        self.index.add(embeddings_np)
        
    def search(self, query_embedding, top_k=5):
        """Search the FAISS index for the top_k nearest neighbors."""
        query_np = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_np, top_k)
        return distances[0], indices[0]

def search_index(query_embedding):
    pass
