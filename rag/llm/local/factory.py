from rag.llm.local.HuggingFaceModel import HuggingFaceModel

llm_model_registry = {
    "qwen3-8b": "Qwen/Qwen3-8B",
    "qwen2.5-7b-instruct": "Qwen/Qwen2.5-7B-Instruct",
    "llama3.1-8b-instruct": "meta-llama/Llama-3.1-8B-Instruct"
}

import os
from rag.config.logger import logger

def get_llm_model(model_name_key: str = None) -> HuggingFaceModel:
    """
    Factory method to instantiate a HuggingFaceLLM with a specified model.

    Uses the model registry to map logical names to HF model identifiers.

    Args:
        model_name_key (str, optional): Logical name of the model to instantiate.
                                        If None, uses the default from env 'LLM_MODEL_NAME_KEY'.

    Returns:
        HuggingFaceLLM: An instance of HuggingFaceLLM with the selected model.

    Raises:
        ValueError: If the specified logical model name is not found in the registry.
    """
    model_name_key = model_name_key or os.getenv("LLM_MODEL_NAME_KEY", "qwen3-8b")
    logger.info(f"[LLM FACTORY]: Using logical model name: {model_name_key}")

    if model_name_key not in llm_model_registry:
        raise ValueError(
            f"Unknown logical model name: '{model_name_key}'. Available: {list(llm_model_registry.keys())}"
        )

    hf_model_name = llm_model_registry[model_name_key]
    return HuggingFaceModel(model_name=hf_model_name)
