"""
Documents Router — AI-Powered Study Buddy
==========================================
Endpoints:
  POST   /documents/upload  → upload + index a file
  GET    /documents/        → list user's documents
  DELETE /documents/{id}    → delete a document + its vectors
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.schemas import DocumentOut, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    """
    Upload a study document (PDF, DOCX, PPTX, TXT).
    Triggers the full ingestion pipeline asynchronously.
    Max file size: 50 MB (enforced in config.toml and validator).
    """
    file_bytes = await file.read()
    return await DocumentService(db).upload_and_index(
        user_id=current_user.id,
        file_bytes=file_bytes,
        filename=file.filename or "upload",
    )


@router.get("/", response_model=list[DocumentOut])
async def list_documents(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentOut]:
    """Return all documents uploaded by the current user."""
    return await DocumentService(db).list_documents(current_user.id)


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a document and its ChromaDB embeddings."""
    await DocumentService(db).delete_document(current_user.id, doc_id)
