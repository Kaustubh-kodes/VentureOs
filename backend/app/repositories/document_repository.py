import logging
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from app.services.supabase_service import supabase_service

logger = logging.getLogger("ventureos.document_repository")


class DocumentRepository:
    def __init__(self):
        self.doc_table = "knowledge_documents"
        self.chunk_table = "document_chunks"

    def _client(self):
        return supabase_service.get_client()

    def create_document(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        client = self._client()
        try:
            logger.info("Inserting knowledge document record: %s", payload.get("filename"))
            res = client.table(self.doc_table).insert(payload).execute()
            if not res.data:
                raise HTTPException(status_code=500, detail="Database returned no record on document insert.")
            return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error creating document in Supabase: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Database error creating document: {str(e)}")

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        client = self._client()
        try:
            res = client.table(self.doc_table).select("*").eq("id", document_id).execute()
            if not res.data or len(res.data) == 0:
                return None
            return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error fetching document %s from Supabase: %s", document_id, str(e))
            raise HTTPException(status_code=500, detail=f"Database error fetching document: {str(e)}")

    def update_document_status(
        self,
        document_id: str,
        status: str,
        total_chunks: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        client = self._client()
        payload: Dict[str, Any] = {"status": status}
        if total_chunks is not None:
            payload["total_chunks"] = total_chunks
        if error_message is not None:
            payload["error_message"] = error_message

        try:
            res = client.table(self.doc_table).update(payload).eq("id", document_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail=f"Document {document_id} not found for update.")
            return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error updating document %s in Supabase: %s", document_id, str(e))
            raise HTTPException(status_code=500, detail=f"Database error updating document: {str(e)}")

    def list_documents(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        client = self._client()
        try:
            query = client.table(self.doc_table).select("*").order("created_at", desc=True)
            if session_id:
                query = query.eq("session_id", session_id)
            res = query.execute()
            return res.data or []
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error listing documents from Supabase: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Database error listing documents: {str(e)}")

    def delete_document(self, document_id: str) -> bool:
        client = self._client()
        try:
            # Foreign key ON DELETE CASCADE will automatically clean document_chunks
            res = client.table(self.doc_table).delete().eq("id", document_id).execute()
            return bool(res.data and len(res.data) > 0)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error deleting document %s in Supabase: %s", document_id, str(e))
            raise HTTPException(status_code=500, detail=f"Database error deleting document: {str(e)}")

    def insert_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        if not chunks:
            return

        client = self._client()
        # Batch insert chunks in batches of 100
        batch_size = 100
        try:
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i : i + batch_size]
                logger.info("Inserting chunk batch of %d items into %s", len(batch), self.chunk_table)
                client.table(self.chunk_table).insert(batch).execute()
        except Exception as e:
            logger.error("Error inserting chunks into Supabase: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Database error storing document chunks: {str(e)}")

    def search_similar_chunks(
        self,
        query_embedding: List[float],
        match_threshold: float = 0.0,
        match_count: int = 5,
        filter_document_id: Optional[str] = None,
        filter_session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Calls PostgreSQL RPC match_document_chunks using pgvector similarity.
        """
        client = self._client()
        params = {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count,
            "filter_document_id": filter_document_id,
            "filter_session_id": filter_session_id,
        }
        try:
            logger.info("Calling match_document_chunks RPC with match_count=%d", match_count)
            res = client.rpc("match_document_chunks", params).execute()
            return res.data or []
        except Exception as e:
            logger.error("Semantic search RPC failed: %s", str(e))
            return []


document_repository = DocumentRepository()
