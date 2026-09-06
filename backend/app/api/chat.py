import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent import runtime as agent_runtime
from app.core.deps import get_current_user
from app.database import get_db
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.message import Message, MessageRole
from app.models.user import User
from app.schemas.chat import (
    AskRequest,
    AskResponse,
    Citation,
    ConversationDetailResponse,
    ConversationResponse,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if payload.document_id is not None:
        document = db.get(Document, payload.document_id)
        if document is None or document.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Document not found")

    conversation = _get_or_create_conversation(db, current_user, payload)

    db.add(Message(conversation_id=conversation.id, role=MessageRole.USER, content=payload.message))
    db.commit()

    try:
        answer, raw_citations = await agent_runtime.ask(
            user_id=current_user.id,
            conversation_id=conversation.id,
            document_id=payload.document_id,
            message=payload.message,
        )
    except Exception as exc:  # noqa: BLE001 - surface upstream LLM/embedding failures as a clean error
        raise HTTPException(status_code=502, detail=f"The assistant is temporarily unavailable: {exc}") from exc

    citations = [
        Citation(
            document_id=uuid.UUID(m["document_id"]),
            document_name=m["document_name"],
            page=m["page"],
            snippet=m["text"][:280],
        )
        for m in raw_citations
    ]

    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=answer,
        citations=[c.model_dump(mode="json") for c in citations] or None,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return AskResponse(conversation_id=conversation.id, message=assistant_message)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


def _get_or_create_conversation(db: Session, user: User, payload: AskRequest) -> Conversation:
    if payload.conversation_id is not None:
        conversation = db.get(Conversation, payload.conversation_id)
        if conversation is None or conversation.user_id != user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation

    conversation = Conversation(
        user_id=user.id,
        document_id=payload.document_id,
        title=payload.message[:80],
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation
