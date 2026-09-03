import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger("ventureos.embedding_service")


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, dimension: int = 768):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.embedding_model or "gemini-embedding-001"
        self.dimension = dimension or settings.embedding_dimension or 768
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        if not self.api_key or "your_gemini" in self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured on the backend for embedding generation.")
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def embed_text(self, text: str) -> List[float]:
        client = self._get_client()
        cfg = types.EmbedContentConfig(output_dimensionality=self.dimension)
        try:
            res = client.models.embed_content(
                model=self.model,
                contents=text,
                config=cfg,
            )
            return res.embeddings[0].values
        except Exception as e:
            logger.error("Gemini embed_text failed: %s", str(e))
            raise ValueError(f"Failed to generate embedding: {str(e)}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        client = self._get_client()
        cfg = types.EmbedContentConfig(output_dimensionality=self.dimension)
        results: List[List[float]] = []

        # Batch in chunks of 50 to avoid API payload caps
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                logger.info("Generating embeddings for batch of %d items (%d/%d)", len(batch), i + len(batch), len(texts))
                res = client.models.embed_content(
                    model=self.model,
                    contents=batch,
                    config=cfg,
                )
                for emb in res.embeddings:
                    results.append(emb.values)
            except Exception as e:
                logger.error("Gemini batch embed_texts failed on items %d-%d: %s", i, i + len(batch), str(e))
                raise ValueError(f"Embedding generation failed: {str(e)}")

        return results


class EmbeddingService:
    def __init__(self):
        self._provider = GeminiEmbeddingProvider()

    def embed_text(self, text: str) -> List[float]:
        return self._provider.embed_text(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self._provider.embed_texts(texts)


embedding_service = EmbeddingService()
