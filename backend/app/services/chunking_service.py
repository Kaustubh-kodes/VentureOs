import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("ventureos.chunking_service")


class ChunkingService:
    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        # Character approximation: ~4 characters per token
        base_tokens = chunk_size or settings.chunk_size or 600
        overlap_tokens = chunk_overlap or settings.chunk_overlap or 100
        self.chunk_char_limit = base_tokens * 4
        self.overlap_char_limit = overlap_tokens * 4

    def chunk_extracted_blocks(
        self,
        blocks: List[Dict[str, Any]],
        document_id: str,
        filename: str,
    ) -> List[Dict[str, Any]]:
        """
        Takes extracted document blocks (pages/sections) and breaks them into
        semantically coherent overlapping chunks.
        Returns:
            List of dicts: [
                {
                    "document_id": str,
                    "chunk_index": int,
                    "content": str,
                    "metadata": {
                        "filename": str,
                        "page": Optional[int],
                        "chunk_index": int
                    }
                }
            ]
        """
        all_chunks: List[Dict[str, Any]] = []
        global_chunk_idx = 0

        for block in blocks:
            text = block.get("text", "")
            page = block.get("page")
            if not text:
                continue

            # Split text into paragraphs
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            current_chunk: List[str] = []
            current_len = 0

            for para in paragraphs:
                para_len = len(para)

                # If paragraph itself exceeds char limit, break into sentence slices
                if para_len > self.chunk_char_limit:
                    sentences = self._split_into_sentences(para)
                    for sent in sentences:
                        sent_len = len(sent)
                        if current_len + sent_len > self.chunk_char_limit and current_chunk:
                            chunk_text = " ".join(current_chunk).strip()
                            if chunk_text:
                                all_chunks.append({
                                    "document_id": document_id,
                                    "chunk_index": global_chunk_idx,
                                    "content": chunk_text,
                                    "metadata": {
                                        "filename": filename,
                                        "page": page,
                                        "chunk_index": global_chunk_idx,
                                    },
                                })
                                global_chunk_idx += 1
                            # Retain overlap from end of current chunk
                            current_chunk = self._get_overlap_tail(current_chunk)
                            current_len = sum(len(c) for c in current_chunk)

                        current_chunk.append(sent)
                        current_len += sent_len
                else:
                    if current_len + para_len > self.chunk_char_limit and current_chunk:
                        chunk_text = "\n\n".join(current_chunk).strip()
                        if chunk_text:
                            all_chunks.append({
                                "document_id": document_id,
                                "chunk_index": global_chunk_idx,
                                "content": chunk_text,
                                "metadata": {
                                    "filename": filename,
                                    "page": page,
                                    "chunk_index": global_chunk_idx,
                                },
                            })
                            global_chunk_idx += 1
                        # Retain overlap from previous chunk
                        current_chunk = self._get_overlap_tail(current_chunk)
                        current_len = sum(len(c) for c in current_chunk)

                    current_chunk.append(para)
                    current_len += para_len

            # Flush remaining chunk in this block
            if current_chunk:
                chunk_text = "\n\n".join(current_chunk).strip()
                if chunk_text:
                    all_chunks.append({
                        "document_id": document_id,
                        "chunk_index": global_chunk_idx,
                        "content": chunk_text,
                        "metadata": {
                            "filename": filename,
                            "page": page,
                            "chunk_index": global_chunk_idx,
                        },
                    })
                    global_chunk_idx += 1

        logger.info("Chunking completed for '%s': generated %d chunks", filename, len(all_chunks))
        return all_chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        # Simple punctuation-aware split
        import re
        parts = re.split(r"(?<=[.?!])\s+", text)
        return [p.strip() for p in parts if p.strip()]

    def _get_overlap_tail(self, items: List[str]) -> List[str]:
        overlap_items: List[str] = []
        accumulated = 0
        for item in reversed(items):
            if accumulated + len(item) <= self.overlap_char_limit:
                overlap_items.insert(0, item)
                accumulated += len(item)
            else:
                break
        return overlap_items


chunking_service = ChunkingService()
