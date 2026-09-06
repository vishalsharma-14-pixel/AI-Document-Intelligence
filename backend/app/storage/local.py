import os
import uuid

from fastapi import UploadFile

from app.config import settings

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls", ".txt", ".md"}


def save_upload(user_id: uuid.UUID, file: UploadFile) -> tuple[str, str]:
    """Persist an uploaded file to disk. Returns (file_path, file_type)."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type '{ext}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}")

    user_dir = os.path.join(settings.upload_dir, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(user_dir, stored_name)

    with open(file_path, "wb") as out:
        while chunk := file.file.read(1024 * 1024):
            out.write(chunk)

    return file_path, ext.lstrip(".")


def delete_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
