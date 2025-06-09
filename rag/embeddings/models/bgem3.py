from FlagEmbedding import BGEM3FlagModel
import torch
from typing import Union
from typing import List, Dict
from rag.embeddings.base import EmbeddingModel
from rag.config.logger import get_logger

logger = get_logger(__name__)

class BGEM3Embedding(EmbeddingModel):
    MAX_INPUT = 8191

    def __init__(self):
        self.device = self._detect_device()
        self.model = BGEM3FlagModel(
            "BAAI/bge-m3",
            use_fp16=self.device == "cuda",
            use_flash_attn=False
        )
        logger.info(f"[EMBEDDING] BGEM3 loaded on {self.device}")

    def _detect_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def encode(
            self,
            text: Union[str, List[str]],
            batch_size: int = 12,
            max_length: int = MAX_INPUT
    ) -> Union[List[float], List[List[float]]]:
        result = self.model.encode(
            text,
            batch_size=batch_size,
            max_length=max_length
        )
        return result['dense_vecs']

    def encode_sparse(
            self,
            text: Union[str, List[str]],
            batch_size: int = 12,
            max_length: int = MAX_INPUT
    ) -> Union[Dict, List[Dict]]:
        result = self.model.encode(
            text,
            batch_size=batch_size,
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False,
            max_length=max_length
        )
        return result["lexical_weights"]

