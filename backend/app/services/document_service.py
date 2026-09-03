import logging
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, BackgroundTasks
from app.services.document_processor import document_processor
from app.services.chunking_service import chunking_service
from app.services.embedding_service import embedding_service
from app.services.supabase_service import supabase_service
from app.repositories.document_repository import document_repository
from app.config import settings

logger = logging.getLogger("ventureos.document_service")


class DocumentService:
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md", "markdown"}

    def upload_document(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        session_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> Dict[str, Any]:
        """
        Validates file, creates document metadata in PostgreSQL, and queues background
        text extraction, chunking, and embedding generation.
        """
        # Step 1: Validate file extension
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '.{ext}'. Supported formats are: PDF, DOCX, TXT, MD.",
            )

        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Max file size: 25 MB
        if len(file_bytes) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds the 25MB limit.")

        # Step 2: Create initial document record with status 'processing'
        doc_payload = {
            "session_id": session_id,
            "filename": filename,
            "file_type": ext,
            "file_size": len(file_bytes),
            "title": title or filename,
            "description": description,
            "storage_path": f"documents/{filename}",
            "status": "processing",
            "total_chunks": 0,
        }
        created_doc = document_repository.create_document(doc_payload)
        doc_id = str(created_doc.get("id"))
        logger.info("Document metadata created with ID: %s. Queueing processing pipeline.", doc_id)

        # Step 3: Run pipeline asynchronously or in background
        if background_tasks:
            background_tasks.add_task(
                self.process_document_pipeline,
                doc_id,
                file_bytes,
                filename,
                ext,
            )
        else:
            # Synchronous fallback if no background tasks provided
            self.process_document_pipeline(doc_id, file_bytes, filename, ext)

        return created_doc

    def process_document_pipeline(
        self,
        document_id: str,
        file_bytes: bytes,
        filename: str,
        file_type: str,
    ) -> None:
        """
        Complete processing pipeline:
        1. Extract text
        2. Clean text
        3. Split into semantic chunks
        4. Generate embeddings with Gemini
        5. Store chunks + vectors in Supabase
        6. Mark document as completed
        """
        logger.info("Starting processing pipeline for document: %s (%s)", document_id, filename)
        try:
            # 1. Extraction & Cleaning
            blocks = document_processor.extract(file_bytes, filename, file_type)
            if not blocks:
                raise ValueError("No extractable content found in document.")

            # 2. Chunking
            chunks = chunking_service.chunk_extracted_blocks(blocks, document_id, filename)
            if not chunks:
                raise ValueError("Document yielded no chunks after semantic splitting.")

            logger.info("Generated %d chunks for document %s. Generating embeddings...", len(chunks), document_id)

            # 3. Embedding Generation
            texts_to_embed = [c["content"] for c in chunks]
            embeddings = embedding_service.embed_texts(texts_to_embed)

            # Attach embeddings to chunks
            chunks_to_insert = []
            for chunk, emb in zip(chunks, embeddings):
                chunks_to_insert.append({
                    "document_id": document_id,
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                    "embedding": emb,
                })

            # 4. Store in database
            document_repository.insert_chunks(chunks_to_insert)

            # 5. Mark document as completed
            document_repository.update_document_status(
                document_id=document_id,
                status="completed",
                total_chunks=len(chunks_to_insert),
            )
            logger.info("Document pipeline completed successfully for %s! Total chunks: %d", document_id, len(chunks_to_insert))

        except Exception as e:
            error_msg = str(e)
            logger.error("Processing pipeline failed for document %s: %s", document_id, error_msg)
            document_repository.update_document_status(
                document_id=document_id,
                status="failed",
                error_message=error_msg[:500],
            )

    def list_documents(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return document_repository.list_documents(session_id=session_id)

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        return document_repository.get_document(document_id)

    def delete_document(self, document_id: str) -> bool:
        return document_repository.delete_document(document_id)


document_service = DocumentService()
