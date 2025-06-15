from abc import ABC, abstractmethod
from typing import List, Dict, Union
import torch

class EmbeddingModel(ABC):
    """
    Abstract base class for all embedding model implementations.

    This interface defines the methods required for encoding text into dense
    or sparse embeddings, ensuring a consistent API for all embedding models
    used in the system.
    """

    @abstractmethod
    def encode(self, text: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
        """
        Encodes the given text(s) into dense embedding(s).

        Args:
            text (Union[str, List[str]]): A single text string or a list of text strings to encode.
            **kwargs: Additional keyword arguments specific to the embedding model implementation.

        Returns:
            Union[List[float], List[List[float]]]: A dense embedding vector (for a single text)
            or a list of dense embedding vectors (for multiple texts).
        """
        pass

    @abstractmethod
    def encode_sparse(self, text: Union[str, List[str]], **kwargs) -> Union[Dict, List[Dict]]:
        """
        Encodes the given text(s) into sparse embedding(s).

        Args:
            text (Union[str, List[str]]): A single text string or a list of text strings to encode.
            **kwargs: Additional keyword arguments specific to the embedding model implementation.

        Returns:
            Union[Dict, List[Dict]]: A sparse embedding representation as a dictionary (for a single text)
            or a list of sparse embeddings (for multiple texts), typically in the format {token_id: weight}.
        """
        pass

    def _detect_device(self) -> str:
        """
        Detects the most suitable device to run the embedding model (CUDA, MPS, or CPU).

        Returns:
            str: The device type ('cuda', 'mps', or 'cpu').
        """
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
