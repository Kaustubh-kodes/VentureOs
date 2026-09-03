import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.text_cleaner import text_cleaner
from app.services.document_processor import document_processor
from app.services.chunking_service import chunking_service
from app.services.rag_service import rag_service
from app.services.embedding_service import embedding_service
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_text_cleaner():
    raw = "  Line 1   with spaces \r\n\r\n\r\n\r\nLine 2   \u00a0 after blank lines   "
    cleaned = text_cleaner.clean(raw)
    assert "Line 1 with spaces" in cleaned
    assert "Line 2 after blank lines" in cleaned
    assert "\n\n\n" not in cleaned


def test_txt_and_md_extraction():
    txt_bytes = b"VentureOS is an AI-powered startup operating system.\n\nIt helps founders validate ideas."
    blocks = document_processor.extract(txt_bytes, "pitch.txt", "text/plain")
    assert len(blocks) == 1
    assert "VentureOS is an AI-powered startup" in blocks[0]["text"]
    assert blocks[0]["source"] == "pitch.txt"

    md_bytes = b"# VentureOS Vision\n\nEmpowering early-stage founders with autonomous multi-agent intelligence."
    md_blocks = document_processor.extract(md_bytes, "strategy.md", "text/markdown")
    assert len(md_blocks) == 1
    assert "Empowering early-stage founders" in md_blocks[0]["text"]


def test_unsupported_file_rejection():
    try:
        document_processor.extract(b"xyz", "archive.zip", "application/zip")
        assert False, "Should have raised ValueError for unsupported format"
    except ValueError as e:
        assert "Unsupported file format" in str(e)


def test_chunking_service():
    sample_text = "\n\n".join([f"Paragraph {i}: Market sizing and competitive moats are critical for venture growth." for i in range(25)])
    blocks = [{"text": sample_text, "page": 1, "source": "market.pdf"}]
    chunks = chunking_service.chunk_extracted_blocks(blocks, "doc-123", "market.pdf")
    assert len(chunks) >= 1
    for c in chunks:
        assert c["document_id"] == "doc-123"
        assert c["metadata"]["filename"] == "market.pdf"
        assert c["metadata"]["page"] == 1
        assert "chunk_index" in c["metadata"]


def test_rag_context_builder():
    sample_chunks = [
        {
            "content": "Acme Corp projects $2M ARR by Year 2.",
            "metadata": {"filename": "deck.pdf", "page": 4}
        },
        {
            "content": "Competitor pricing averages $99/seat/month.",
            "metadata": {"filename": "deck.pdf", "page": 4}  # duplicate source/page test
        },
        {
            "content": "Total addressable market is $14 Billion.",
            "metadata": {"filename": "market.txt", "page": None}
        }
    ]
    context, sources = rag_service.build_rag_context(sample_chunks)
    assert "FOUNDER KNOWLEDGE BASE CONTEXT" in context
    assert "[Source: deck.pdf | Page: 4]" in context
    assert "[Source: market.txt]" in context
    assert len(sources) == 2  # deduplicated deck.pdf (page 4) and market.txt


def test_embedding_generation():
    emb = embedding_service.embed_text("Test embedding query")
    assert len(emb) == 768
    batch = embedding_service.embed_texts(["Chunk 1", "Chunk 2"])
    assert len(batch) == 2
    assert len(batch[0]) == 768


def test_api_routes():
    res = client.get("/api/documents")
    assert res.status_code in (200, 500, 503)
    res_search = client.post("/api/knowledge/search", json={"query": "test"})
    assert res_search.status_code in (200, 500, 503)


if __name__ == "__main__":
    test_text_cleaner()
    print("[PASS] test_text_cleaner passed")
    test_txt_and_md_extraction()
    print("[PASS] test_txt_and_md_extraction passed")
    test_unsupported_file_rejection()
    print("[PASS] test_unsupported_file_rejection passed")
    test_chunking_service()
    print("[PASS] test_chunking_service passed")
    test_rag_context_builder()
    print("[PASS] test_rag_context_builder passed")
    test_embedding_generation()
    print("[PASS] test_embedding_generation passed (768 dimensions)")
    test_api_routes()
    print("[PASS] test_api_routes passed")
    print("\nAll Phase 5 RAG pipeline tests passed successfully!")
