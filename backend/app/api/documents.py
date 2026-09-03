import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Query
from app.schemas.document import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentListResponse,
    DocumentStatusResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    ChunkSearchResult,
)
from app.services.document_service import document_service
from app.services.rag_service import rag_service

logger = logging.getLogger("ventureos.api.documents")

router = APIRouter(tags=["Knowledge Base & Documents"])


@router.post("/api/documents/upload", response_model=DocumentUploadResponse)
@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
):
    """
    Upload a founder document (PDF, DOCX, TXT, MD) to the knowledge base.
    Extraction, semantic chunking, and pgvector embeddings are processed asynchronously.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    # PART 12: File Upload Hardening
    from pathlib import Path
    import re
    from app.config import settings

    raw_filename = Path(file.filename).name
    clean_filename = re.sub(r"[^\w\-_\.]", "_", raw_filename)
    ext = Path(clean_filename).suffix.lower()

    if ext not in settings.allowed_file_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(settings.allowed_file_extensions)}",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(file_bytes) > settings.max_upload_size_bytes:
        max_mb = settings.max_upload_size_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum upload limit of {max_mb} MB.",
        )

    doc = document_service.upload_document(
        file_bytes=file_bytes,
        filename=clean_filename,
        content_type=file.content_type or "application/octet-stream",
        session_id=session_id,
        title=title,
        description=description,
        background_tasks=background_tasks,
    )

    return DocumentUploadResponse(
        success=True,
        id=str(doc.get("id")),
        filename=doc.get("filename"),
        file_type=doc.get("file_type"),
        file_size=doc.get("file_size"),
        status=doc.get("status", "processing"),
        total_chunks=doc.get("total_chunks", 0),
        message="Document uploaded successfully and queued for processing",
    )


@router.get("/api/documents", response_model=DocumentListResponse)
@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(session_id: Optional[str] = Query(None, description="Optional session filter")):
    """
    List all uploaded documents in the knowledge base.
    """
    records = document_service.list_documents(session_id=session_id)
    docs = [
        DocumentResponse(
            id=str(r.get("id")),
            session_id=str(r.get("session_id")) if r.get("session_id") else None,
            filename=r.get("filename"),
            file_type=r.get("file_type"),
            file_size=r.get("file_size"),
            title=r.get("title"),
            description=r.get("description"),
            storage_path=r.get("storage_path"),
            status=r.get("status"),
            total_chunks=r.get("total_chunks", 0),
            error_message=r.get("error_message"),
            created_at=str(r.get("created_at")) if r.get("created_at") else None,
            updated_at=str(r.get("updated_at")) if r.get("updated_at") else None,
        )
        for r in records
    ]
    return DocumentListResponse(success=True, total=len(docs), documents=docs)


@router.get("/api/documents/{document_id}", response_model=DocumentResponse)
@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """
    Get detailed metadata for a single document.
    """
    r = document_service.get_document(document_id)
    if not r:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    return DocumentResponse(
        id=str(r.get("id")),
        session_id=str(r.get("session_id")) if r.get("session_id") else None,
        filename=r.get("filename"),
        file_type=r.get("file_type"),
        file_size=r.get("file_size"),
        title=r.get("title"),
        description=r.get("description"),
        storage_path=r.get("storage_path"),
        status=r.get("status"),
        total_chunks=r.get("total_chunks", 0),
        error_message=r.get("error_message"),
        created_at=str(r.get("created_at")) if r.get("created_at") else None,
        updated_at=str(r.get("updated_at")) if r.get("updated_at") else None,
    )


@router.get("/api/documents/{document_id}/status", response_model=DocumentStatusResponse)
@router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: str):
    """
    Poll processing status of an uploaded document.
    """
    r = document_service.get_document(document_id)
    if not r:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    return DocumentStatusResponse(
        success=True,
        id=str(r.get("id")),
        filename=r.get("filename"),
        status=r.get("status"),
        total_chunks=r.get("total_chunks", 0),
        error_message=r.get("error_message"),
    )


@router.delete("/api/documents/{document_id}")
@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and cascade delete its chunks and vector embeddings.
    """
    existing = document_service.get_document(document_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    success = document_service.delete_document(document_id)
    return {"success": success, "message": f"Document '{document_id}' deleted successfully."}


@router.post("/api/knowledge/search", response_model=KnowledgeSearchResponse)
@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(request: KnowledgeSearchRequest):
    """
    Developer/debug endpoint for semantic similarity search over document chunks.
    """
    chunks = rag_service.retrieve_context(
        query=request.query,
        session_id=request.session_id,
        document_id=request.document_id,
        top_k=request.top_k,
    )

    results = []
    for c in chunks:
        meta = c.get("metadata") or {}
        results.append(
            ChunkSearchResult(
                id=str(c.get("id")),
                document_id=str(c.get("document_id")),
                filename=meta.get("filename"),
                page=meta.get("page"),
                chunk_index=c.get("chunk_index", 0),
                content=c.get("content", ""),
                similarity=float(c.get("similarity", 0.0)),
                metadata=meta,
            )
        )

    return KnowledgeSearchResponse(
        success=True,
        query=request.query,
        total=len(results),
        results=results,
    )
