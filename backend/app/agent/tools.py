import uuid

from app.config import settings
from app.services import embeddings, vectorstore


def make_search_documents_tool(
    user_id: uuid.UUID,
    document_id: uuid.UUID | None,
    citations_sink: list[dict],
):
    """Builds a `search_documents` tool scoped to one user (and optionally one
    document), so the LLM can never be steered into searching another user's
    data. Matches returned by the tool are also appended to `citations_sink`
    so the API layer can build structured citations independent of how the
    model formats its answer text."""

    def search_documents(query: str) -> dict:
        """Search the user's uploaded documents for passages relevant to a query.

        Always call this before answering a question about the user's documents
        — never answer from general knowledge.

        Args:
            query (str): A question or topic to search for in the uploaded documents.

        Returns:
            dict: status, and either matching passages or an error message.
        """
        query_embedding = embeddings.embed_query(query)
        matches = vectorstore.query(user_id, query_embedding, settings.retrieval_top_k, document_id)
        if not matches:
            return {
                "status": "error",
                "error_message": "No relevant passages were found in the uploaded documents.",
            }
        citations_sink.extend(matches)
        return {
            "status": "success",
            "matches": [
                {
                    "document_name": m["document_name"],
                    "page": m["page"],
                    "section": m["section"],
                    "text": m["text"],
                }
                for m in matches
            ],
        }

    return search_documents
