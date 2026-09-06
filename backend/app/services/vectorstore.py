import uuid

import chromadb

from app.config import settings

# Created lazily (not at import time): Celery's prefork pool imports this module in
# the parent process and then forks worker children. A client created pre-fork can
# hang forever on first use in a forked child if it holds any native background-
# thread state. Building it on first use inside the (already forked) worker avoids
# that entirely.
#
# This talks to the standalone Chroma server (see docker-compose.yml) over HTTP,
# rather than opening the on-disk index directly (chromadb.PersistentClient), because
# the API process and the Celery worker process both need to read/write the same
# data - and a PersistentClient's view of the index is not safely shared across two
# OS processes pointed at the same directory.
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return _client


def _collection_name(user_id: uuid.UUID) -> str:
    return f"user_{user_id}"


def _get_collection(user_id: uuid.UUID):
    return _get_client().get_or_create_collection(
        name=_collection_name(user_id),
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(
    user_id: uuid.UUID,
    document_id: uuid.UUID,
    document_name: str,
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:
    if not chunks:
        return
    collection = _get_collection(user_id)
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "document_id": str(document_id),
            "document_name": document_name,
            "page": chunk["page"] if chunk.get("page") is not None else -1,
            "section": chunk.get("section") or "",
            "chunk_index": i,
        }
        for i, chunk in enumerate(chunks)
    ]
    documents = [chunk["text"] for chunk in chunks]
    collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def query(
    user_id: uuid.UUID,
    query_embedding: list[float],
    top_k: int,
    document_id: uuid.UUID | None = None,
) -> list[dict]:
    collection = _get_collection(user_id)
    if collection.count() == 0:
        return []
    where = {"document_id": str(document_id)} if document_id else None
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k, where=where)

    matches = []
    for doc, meta, distance in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        matches.append(
            {
                "text": doc,
                "document_id": meta["document_id"],
                "document_name": meta["document_name"],
                "page": None if meta["page"] == -1 else meta["page"],
                "section": meta["section"] or None,
                "similarity": 1 - distance,
            }
        )
    return matches


def delete_document(user_id: uuid.UUID, document_id: uuid.UUID) -> None:
    collection = _get_collection(user_id)
    collection.delete(where={"document_id": str(document_id)})


def get_document_chunks(user_id: uuid.UUID, document_id: uuid.UUID) -> list[dict]:
    """All chunks for one document, ordered by chunk_index (used for summarization)."""
    collection = _get_collection(user_id)
    if collection.count() == 0:
        return []
    result = collection.get(where={"document_id": str(document_id)})
    rows = sorted(
        zip(result["documents"], result["metadatas"]),
        key=lambda pair: pair[1]["chunk_index"],
    )
    return [{"text": text, "page": None if meta["page"] == -1 else meta["page"]} for text, meta in rows]
