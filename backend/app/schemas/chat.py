import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.message import MessageRole


class AskRequest(BaseModel):
    message: str
    conversation_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None


class Citation(BaseModel):
    document_id: uuid.UUID
    document_name: str
    page: int | None = None
    snippet: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: MessageRole
    content: str
    citations: list[Citation] | None
    created_at: datetime


class AskResponse(BaseModel):
    conversation_id: uuid.UUID
    message: MessageResponse


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID | None
    title: str | None
    created_at: datetime


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse]
