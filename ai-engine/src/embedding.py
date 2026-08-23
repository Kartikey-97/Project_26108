from sentence_transformers import SentenceTransformer

# Load a pre-trained sentence transformer model
_model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(text):
    """Generates embeddings for the given text using SentenceTransformers."""
    if isinstance(text, str):
        return _model.encode([text])[0]
    elif isinstance(text, list):
        return _model.encode(text)
    return None

