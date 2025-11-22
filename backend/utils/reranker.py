"""Cross-encoder based reranking utility using sentence-transformers models (e.g., BAAI/bge-reranker-base)."""
from typing import List, Tuple
from functools import lru_cache
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
import config


@lru_cache(maxsize=1)
def _get_model(model_name: str):
    return CrossEncoder(model_name)


def rerank(query: str, docs: List[Document], model_name: str = None, top_k: int = None) -> List[Document]:
    if not docs:
        return []
    model_name = model_name or config.RERANK_MODEL_NAME
    top_k = top_k or config.RERANK_TOP_K
    model = _get_model(model_name)
    pairs: List[Tuple[str, str]] = [(query, d.page_content) for d in docs]
    scores = model.predict(pairs)
    scored = list(zip(docs, scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [d for d, _ in scored[:top_k]]

__all__ = ["rerank"]
