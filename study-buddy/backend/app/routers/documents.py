"""
Documents Router — AI-Powered Study Buddy
==========================================
Endpoints:
  POST   /documents/upload  → upload + index a file (returns 202 immediately)
  GET    /documents/        → list user's documents
  GET    /documents/{id}/status → poll indexing status
  DELETE /documents/{id}    → delete a document + its vectors
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.schemas import DocumentOut, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    """
    Upload a study document (PDF, DOCX, PPTX, TXT).

    Returns 202 Accepted immediately after saving the file and creating the
    DB record.  Text extraction, chunking, and embedding run in the background.
    Poll GET /documents/{id}/status to check when status changes to 'ready'.

    Max file size: 50 MB (enforced in file validator).
    """
    file_bytes = await file.read()
    svc = DocumentService(db)

    # Creates DB record + saves file — fast (< 100 ms)
    pending = await svc.accept_upload(
        user_id=current_user.id,
        file_bytes=file_bytes,
        filename=file.filename or "upload",
    )

    # Heavy work (extract → chunk → embed → store) runs after response is sent
    background_tasks.add_task(
        svc.index_document,
        doc_id=pending.id,
        user_id=current_user.id,
    )

    return pending


@router.get("/{doc_id}/status")
async def document_status(
    doc_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Poll the indexing status of a document (processing | ready | error)."""
    return await DocumentService(db).get_status(current_user.id, doc_id)


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
