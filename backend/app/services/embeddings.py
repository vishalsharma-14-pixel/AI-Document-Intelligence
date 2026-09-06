"""Gemini embeddings, kept behind a small interface so this is a one-file swap
to a local sentence-transformers model if the free tier ever prompts for billing."""

from google import genai

from app.config import settings

# Created lazily, not at import time - see the comment in services/vectorstore.py:
# a client built pre-fork in Celery's parent process can hang forever on first use
# in a forked worker child if it holds any native background-thread state.
_client = None

# Gemini's embedContent endpoint accepts a limited batch size per request.
_BATCH_SIZE = 100


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.google_api_key)
    return _client


def embed(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    vectors: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        response = _get_client().models.embed_content(model=settings.embedding_model, contents=batch)
        vectors.extend(embedding.values for embedding in response.embeddings)
    return vectors


def embed_query(text: str) -> list[float]:
    return embed([text])[0]
