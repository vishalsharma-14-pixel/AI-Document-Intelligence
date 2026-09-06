import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentSummaryResponse
from app.services import summarizer, vectorstore
from app.storage.local import delete_file, save_upload
from app.tasks.process_document import process_document_task

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        file_path, file_type = save_upload(current_user.id, file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    document = Document(
        user_id=current_user.id,
        filename=file.filename or "untitled",
        file_path=file_path,
        file_type=file_type,
        status=DocumentStatus.PENDING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    process_document_task.delay(str(document.id))

    return document


@router.get("", response_model=list[DocumentResponse])
def list_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return _get_owned_document(db, current_user.id, document_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    document_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    document = _get_owned_document(db, current_user.id, document_id)
    vectorstore.delete_document(current_user.id, document.id)
    delete_file(document.file_path)
    db.delete(document)
    db.commit()


@router.post("/{document_id}/summary", response_model=DocumentSummaryResponse)
def summarize_document(
    document_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    document = _get_owned_document(db, current_user.id, document_id)
    if document.status != DocumentStatus.READY:
        raise HTTPException(status_code=409, detail="Document is still processing or failed")

    if not document.summary:
        try:
            document.summary = summarizer.summarize_document(current_user.id, document.id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001 - surface upstream LLM failures as a clean error
            raise HTTPException(status_code=502, detail=f"The summarizer is temporarily unavailable: {exc}") from exc
        db.commit()

    return DocumentSummaryResponse(id=document.id, summary=document.summary)


def _get_owned_document(db: Session, user_id: uuid.UUID, document_id: uuid.UUID) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.user_id != user_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
