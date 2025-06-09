from rag.embeddings.models.bgem3 import BGEM3Embedding
from rag.embeddings.models.e5_bm25 import E5BM25Embedding, logger
from rag.embeddings.base import EmbeddingModel
from rag.config.settings import settings


embedding_registry = {
    "bge-m3": BGEM3Embedding,
    "e5_bm25": E5BM25Embedding,  # ← puedes añadir más aquí en el futuro
}


def get_embedding_model(model_name: str = None) -> EmbeddingModel:
    """
    Factory method to instantiate an embedding model by name.
    """
    model_name = model_name or settings.embedding_model
    logger.info(f"[EMBEDDING MODEL]: Using embedding model: {model_name}")

    if model_name not in embedding_registry:
        raise ValueError(
            f"Unknown embedding model: '{model_name}'. Available: {list(embedding_registry.keys())}"
        )

    return embedding_registry[model_name]()
