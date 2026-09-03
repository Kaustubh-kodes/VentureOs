from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class DocumentUploadResponse(BaseModel):
    success: bool = True
    id: str
    filename: str
    file_type: str
    file_size: Optional[int] = None
    status: str
    total_chunks: int = 0
    message: str = "Document uploaded successfully and queued for processing"


class DocumentResponse(BaseModel):
    id: str
    session_id: Optional[str] = None
    filename: str
    file_type: str
    file_size: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    storage_path: Optional[str] = None
    status: str
    total_chunks: int = 0
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DocumentListResponse(BaseModel):
    success: bool = True
    total: int
    documents: List[DocumentResponse]


class DocumentStatusResponse(BaseModel):
    success: bool = True
    id: str
    filename: str
    status: str
    total_chunks: int
    error_message: Optional[str] = None


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Semantic search query")
    session_id: Optional[str] = None
    document_id: Optional[str] = None
    top_k: int = 5


class ChunkSearchResult(BaseModel):
    id: str
    document_id: str
    filename: Optional[str] = None
    page: Optional[int] = None
    chunk_index: int
    content: str
    similarity: float
    metadata: Dict[str, Any] = {}


class KnowledgeSearchResponse(BaseModel):
    success: bool = True
    query: str
    total: int
    results: List[ChunkSearchResult]
