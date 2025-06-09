from typing import List, Dict
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding
from rag.embeddings.base import EmbeddingModel
from rag.config.logger import get_logger
from typing import Union

logger = get_logger(__name__)


class E5BM25Embedding(EmbeddingModel):
    MAX_INPUT = 8191

    def __init__(self):
        self.device = self._detect_device()
        self.dense_model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
        self.sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")
        logger.info("E5BM25Embedding: Loaded dense E5 + sparse BM25FastEmbedModel")

    def _detect_device(self) -> str:
        import torch  # Asegúrate de importar torch aquí o al inicio del archivo
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def encode(self, text: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
        if self.dense_model is None:
            raise RuntimeError("Dense model not initialized.")

        if isinstance(text, list):
            return self.dense_model.encode(
                text,
                convert_to_tensor=False,
                max_length=self.MAX_INPUT
            )
        else:
            return self.dense_model.encode(
                text,
                convert_to_tensor=False,
                max_length=self.MAX_INPUT
            )

    def encode_sparse(self, text: Union[str, List[str]], **kwargs) -> Union[Dict, List[Dict]]:
        if self.sparse_model is None:
            raise RuntimeError("Sparse model not initialized.")

        if isinstance(text, list):
            result = []
            for t in text:
                sparse = list(self.sparse_model.embed([t]))[0]
                result.append({
                    str(idx): float(val)
                    for idx, val in zip(sparse.indices.tolist(), sparse.values.tolist())
                })
            return result
        else:
            sparse = list(self.sparse_model.embed([text]))[0]
            return {
                str(idx): float(val)
                for idx, val in zip(sparse.indices.tolist(), sparse.values.tolist())
            }
