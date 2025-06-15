from FlagEmbedding import BGEM3FlagModel
import torch
from typing import Union
from typing import List, Dict
from rag.embeddings.base import EmbeddingModel
from rag.config.logger import logger


class BGEM3Embedding(EmbeddingModel):
    MAX_INPUT = 8191

    def __init__(self):
        self.device = self._detect_device()
        self.model = BGEM3FlagModel(
            "BAAI/bge-m3",
            use_fp16=self.device == "cuda",
            use_flash_attn=False
        )
        logger.info(f"[BGEM3-EMBEDDING]: BGEM3 loaded on {self.device}")

    def encode(
            self,
            text: Union[str, List[str]],
            batch_size: int = 12,
            max_length: int = MAX_INPUT
    ) -> Union[List[float], List[List[float]]]:
        """
        Generates dense embeddings for the given input text(s).

        Args:
            text (Union[str, List[str]]): A single string or a list of strings to encode.
            batch_size (int, optional): Batch size for encoding. Default is 12.
            max_length (int, optional): Maximum length of input tokens. Default is MAX_INPUT.

        Returns:
            Union[List[float], List[List[float]]]: Dense embedding vector(s) for the input.
        """
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
        """
        Generates sparse embeddings for the given input text(s).

        Args:
            text (Union[str, List[str]]): A single string or a list of strings to encode.
            batch_size (int, optional): Batch size for encoding. Default is 12.
            max_length (int, optional): Maximum length of input tokens. Default is MAX_INPUT.

        Returns:
            Union[Dict, List[Dict]]: Sparse embedding(s) in dictionary format (token_id: weight).
        """
        result = self.model.encode(
            text,
            batch_size=batch_size,
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False,
            max_length=max_length
        )
        return result["lexical_weights"]

