from abc import ABC, abstractmethod
from typing import List, Dict, Union

class EmbeddingModel(ABC):
    @abstractmethod
    def encode(self, text: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
        pass

    @abstractmethod
    def encode_sparse(self, text: Union[str, List[str]], **kwargs) -> Union[Dict, List[Dict]]:
        pass
