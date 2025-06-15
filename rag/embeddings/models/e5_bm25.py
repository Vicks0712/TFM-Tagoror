from typing import List, Dict
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding
import torch
from typing import Union

from rag.config.logger import logger
from rag.embeddings.base import EmbeddingModel



class E5BM25Embedding(EmbeddingModel):
    MAX_INPUT = 8191

    def __init__(self):
        self.device = self._detect_device()
        self.dense_model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
        self.sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")
        logger.info("[E5BM25-EMBEDDING]: Loaded dense E5 + sparse BM25FastEmbedModel")


    def encode(self, text: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
        """
        Generates dense embeddings for the given input text(s) using the E5 model.

        Args:
            text (Union[str, List[str]]): A single string or a list of strings to encode.
            **kwargs: Additional keyword arguments (not used in this implementation).

        Returns:
            Union[List[float], List[List[float]]]: Dense embedding vector(s) for the input.
        """
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
        """
        Generates sparse embeddings for the given input text(s) using the BM25 model.

        Args:
            text (Union[str, List[str]]): A single string or a list of strings to encode.
            **kwargs: Additional keyword arguments (not used in this implementation).

        Returns:
            Union[Dict, List[Dict]]: Sparse embedding(s) as dictionaries with token_id: weight pairs.
        """
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
