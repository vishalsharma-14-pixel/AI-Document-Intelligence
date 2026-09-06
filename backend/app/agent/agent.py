from typing import Callable

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from app.config import settings

INSTRUCTION = (
    "You are a document intelligence assistant. The user has uploaded documents "
    "that have been indexed for search. For every user question, ALWAYS call the "
    "`search_documents` tool first — never answer from general knowledge. Base your "
    "answer strictly on the passages the tool returns.\n\n"
    "After your answer, add a line 'Sources:' followed by one bullet per passage "
    "you actually used, formatted as '- <document_name>, page <page>' (omit the "
    "page if it is not available).\n\n"
    "If the tool returns no relevant passages, tell the user you couldn't find an "
    "answer in their uploaded documents rather than guessing."
)


def build_agent(search_documents_tool: Callable) -> Agent:
    return Agent(
        name="doc_intelligence_agent",
        # include_reasoning=False: gpt-oss's reasoning trace gets echoed back as
        # `reasoning_content` on the next turn's message history, which Groq's API
        # then rejects as an unsupported field on assistant messages - a known
        # multi-turn/tool-calling gap for reasoning models proxied through LiteLLM.
        # Turning reasoning output off at the source avoids it entirely.
        model=LiteLlm(model=settings.groq_model, api_key=settings.groq_api_key, include_reasoning=False),
        description="Answers questions about the user's uploaded documents with citations.",
        instruction=INSTRUCTION,
        tools=[search_documents_tool],
    )
