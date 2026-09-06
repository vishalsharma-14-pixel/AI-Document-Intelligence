import uuid

import litellm

from app.config import settings
from app.services import vectorstore

# Groq's free-tier Llama 3.3 70B has a large context window; for demo-sized documents
# a single-pass summary over the concatenated chunks is enough (no map-reduce needed).
_MAX_CONTEXT_CHARS = 24_000

_SUMMARY_PROMPT = (
    "You are a document summarization assistant. Summarize the following document "
    "excerpt in 4-8 concise sentences, covering its main topics and key points. "
    "Only use information present in the text below.\n\n---\n\n{content}"
)


def summarize_document(user_id: uuid.UUID, document_id: uuid.UUID) -> str:
    chunks = vectorstore.get_document_chunks(user_id, document_id)
    if not chunks:
        raise ValueError("No processed content found for this document")

    content = ""
    for chunk in chunks:
        if len(content) + len(chunk["text"]) > _MAX_CONTEXT_CHARS:
            break
        content += chunk["text"] + "\n\n"

    response = litellm.completion(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        messages=[{"role": "user", "content": _SUMMARY_PROMPT.format(content=content.strip())}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
