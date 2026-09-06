import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    file_type: str
    status: DocumentStatus
    error_message: str | None
    page_count: int | None
    chunk_count: int | None
    created_at: datetime
    updated_at: datetime


class DocumentSummaryResponse(BaseModel):
    id: uuid.UUID
    summary: str
