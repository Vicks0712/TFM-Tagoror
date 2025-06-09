from FlagEmbedding import FlagReranker

_reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)

def rerank_documents(query: str, documents: list[dict], top_k: int = None) -> list[dict]:
    if not documents:
        return []

    pairs = [[query, doc["text"]] for doc in documents]
    scores = _reranker.compute_score(pairs, normalize=True)

    for i, doc in enumerate(documents):
        doc["rerank_score"] = scores[i]

    sorted_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
    return sorted_docs[:top_k] if top_k else sorted_docs
