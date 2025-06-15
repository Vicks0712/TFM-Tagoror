import os
import time
from typing import Optional
from fastapi import Request

from rag.components.prompts import build_user_prompt
from rag.components.reranker import rerank_documents
from rag.databases.qdrant.client import qdrant_client
from rag.databases.qdrant.collections import QdrantCollection


async def generate_response_service(
    request: Request,
    collection_name: str,
    question: Optional[str]
):
    start_time = time.time()
    qdrant_collection = QdrantCollection(
        db_client=qdrant_client,
        collection_name=collection_name,
        vector_size=os.getenv("EMBEDDING_VECTOR_SIZE", 1024),
        type=os.getenv("EMBEDDING_SEARCH_TYPE", "hybrid"),
    )
    embedding_model = request.app.state.embedding_model
    llm_model = request.app.state.llm_model

    if os.getenv("EMBEDDING_SEARCH_TYPE") == "hybrid":
        dense_embedding = embedding_model[0].encode(question, max_length=8000)
        sparse_embedding = embedding_model[1].encode(question)
        embedding = {"dense": dense_embedding, "sparse": sparse_embedding}
    else:
        embedding = embedding_model.encode(question)

    n_retrieved = max(os.getenv("N_RERANK", 20), 50)
    most_similar = qdrant_collection.find_most_similar(query_embedding=embedding, n=n_retrieved)
    most_similar = rerank_documents(question, most_similar, top_k=os.getenv("N_RETRIEVED", 7))
    most_similar_context = [item['text'] for item in most_similar]
    formatted_context = "\n\n".join(
        [f"[Documento {i + 1}]\n{doc}" for i, doc in enumerate(most_similar_context)])
    user_prompt = build_user_prompt(question, formatted_context)
    model_answer = llm_model.infer(messages=user_prompt, max_new_tokens=1024)
    elapsed = time.time() - start_time
    return model_answer, elapsed, user_prompt





