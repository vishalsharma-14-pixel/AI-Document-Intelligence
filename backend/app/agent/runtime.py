import uuid

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from app.agent.agent import build_agent
from app.agent.tools import make_search_documents_tool

APP_NAME = "ai-document-intelligence"

# Process-wide session store: conversation memory lives for the life of the
# backend process. Durable transcript/citations still live in Postgres
# (see api/chat.py) - this only powers same-process multi-turn context.
_session_service = InMemorySessionService()


async def ask(
    *,
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    document_id: uuid.UUID | None,
    message: str,
) -> tuple[str, list[dict]]:
    """Runs the document-intelligence agent for one turn.

    Returns (answer_text, citations) where citations are the raw vector-store
    matches the agent's search_documents tool retrieved.
    """
    citations: list[dict] = []
    search_documents_tool = make_search_documents_tool(user_id, document_id, citations)
    agent = build_agent(search_documents_tool)

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=_session_service,
        auto_create_session=True,
    )

    new_message = types.Content(role="user", parts=[types.Part(text=message)])

    answer = ""
    async for event in runner.run_async(
        user_id=str(user_id),
        session_id=str(conversation_id),
        new_message=new_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            answer = "".join(part.text or "" for part in event.content.parts)

    if not answer:
        answer = "I couldn't generate a response. Please try again."

    return answer, citations
