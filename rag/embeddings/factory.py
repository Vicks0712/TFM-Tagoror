import os

from rag.embeddings.models.bgem3 import BGEM3Embedding
from rag.embeddings.models.e5_bm25 import E5BM25Embedding, logger
from rag.embeddings.base import EmbeddingModel


embedding_registry = {
    "bge-m3": BGEM3Embedding,
    "e5_bm25": E5BM25Embedding,
}


def get_embedding_model(model_name: str = None) -> EmbeddingModel:
    """
    Factory method to instantiate an embedding model by name.

    This method looks up the embedding model in the registry and returns
    an instance of the corresponding embedding model class. If no model
    name is provided, it uses the default from the environment variable
    'EMBEDDING_MODEL', falling back to 'e5_bm25'.

    Args:
        model_name (str, optional): Name of the embedding model to instantiate.
                                    If None, uses the default from environment variables.

    Returns:
        EmbeddingModel: An instance of the requested embedding model.

    Raises:
        ValueError: If the specified model name is not found in the registry.
    """
    model_name = model_name or os.getenv("EMBEDDING_MODEL", "e5_bm25")
    logger.info(f"[EMBEDDING MODEL]: Using embedding model: {model_name}")

    if model_name not in embedding_registry:
        raise ValueError(
            f"Unknown embedding model: '{model_name}'. Available: {list(embedding_registry.keys())}"
        )

    return embedding_registry[model_name]()
