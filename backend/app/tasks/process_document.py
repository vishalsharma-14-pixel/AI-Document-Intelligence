import logging

from app.config import settings
from app.database import SessionLocal
from app.models.document import Document, DocumentStatus
from app.services import embeddings, vectorstore
from app.services.chunking import chunk_units
from app.services.parsing import ParsingError, parse_document
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="process_document")
def process_document_task(document_id: str) -> None:
    db = SessionLocal()
    try:
        document = db.get(Document, document_id)
        if document is None:
            logger.warning("process_document_task: document %s not found", document_id)
            return

        document.status = DocumentStatus.PROCESSING
        db.commit()

        try:
            units, page_count = parse_document(document.file_path, document.file_type)
            chunks = chunk_units(units, settings.chunk_size, settings.chunk_overlap)
            if not chunks:
                raise ParsingError("Document produced no usable text chunks")

            vectors = embeddings.embed([c["text"] for c in chunks])
            vectorstore.add_chunks(
                user_id=document.user_id,
                document_id=document.id,
                document_name=document.filename,
                chunks=chunks,
                embeddings=vectors,
            )

            document.status = DocumentStatus.READY
            document.page_count = page_count
            document.chunk_count = len(chunks)
            document.error_message = None
        except ParsingError as exc:
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)
        except Exception as exc:  # noqa: BLE001 - surface any failure as a readable status, don't crash the worker
            logger.exception("process_document_task failed for %s", document_id)
            document.status = DocumentStatus.FAILED
            document.error_message = f"Processing failed: {exc}"

        db.commit()
    finally:
        db.close()
