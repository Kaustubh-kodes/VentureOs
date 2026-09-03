import logging
from typing import List, Dict, Any, Optional, Tuple
from app.services.embedding_service import embedding_service
from app.repositories.document_repository import document_repository
from app.config import settings

logger = logging.getLogger("ventureos.rag_service")


class RAGService:
    def retrieve_context(
        self,
        query: str,
        session_id: Optional[str] = None,
        document_id: Optional[str] = None,
        top_k: Optional[int] = None,
        match_threshold: float = 0.25,
    ) -> List[Dict[str, Any]]:
        """
        Performs semantic similarity search against pgvector document chunks.
        """
        k = top_k or settings.rag_top_k or 5
        if not query or not query.strip():
            return []

        logger.info("Retrieving knowledge chunks for query: '%s' (top_k=%d, session_id=%s)", query[:60], k, session_id)
        try:
            query_embedding = embedding_service.embed_text(query.strip())
            chunks = document_repository.search_similar_chunks(
                query_embedding=query_embedding,
                match_threshold=match_threshold,
                match_count=k,
                filter_document_id=document_id,
                filter_session_id=session_id,
            )
            logger.info("Found %d relevant chunks from knowledge base", len(chunks))
            return chunks
        except Exception as e:
            logger.error("Error during semantic chunk retrieval: %s", str(e))
            return []

    def build_rag_context(self, chunks: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Converts retrieved chunks into an isolated context block for agent prompting
        and compiles a deduplicated list of source references.
        """
        if not chunks:
            return "", []

        context_lines: List[str] = ["FOUNDER KNOWLEDGE BASE CONTEXT (Retrieved Founder Documents):"]
        sources_used: List[Dict[str, Any]] = []
        seen_sources = set()

        for chunk in chunks:
            meta = chunk.get("metadata") or {}
            filename = meta.get("filename") or "Document"
            page = meta.get("page")
            content = chunk.get("content", "").strip()

            source_header = f"[Source: {filename}"
            if page:
                source_header += f" | Page: {page}"
            source_header += "]"

            context_lines.append(source_header)
            context_lines.append(content)
            context_lines.append("---")

            # Track source for frontend attribution
            source_key = f"{filename}_{page}"
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                sources_used.append({
                    "document": filename,
                    "page": page,
                })

        formatted_context = "\n".join(context_lines)
        return formatted_context, sources_used

    def build_retrieval_query(
        self,
        startup_idea: str,
        industry: str,
        target_audience: str,
        budget: str,
        timeline: str,
    ) -> str:
        """
        Generates a composite query representing the venture's core strategic pillars.
        """
        return f"{startup_idea}. Industry: {industry}. Target Audience: {target_audience}. Budget: {budget}. Timeline: {timeline}."


rag_service = RAGService()
