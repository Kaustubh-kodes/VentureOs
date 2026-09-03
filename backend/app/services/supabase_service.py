import logging
from typing import Optional
from fastapi import HTTPException
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger("ventureos.supabase_service")


class SupabaseService:
    def __init__(self):
        self._client: Optional[Client] = None

    @property
    def is_configured(self) -> bool:
        url = settings.supabase_url
        key = settings.supabase_key
        if not url or not key:
            return False
        if "your_supabase" in url or "your_supabase" in key:
            return False
        return bool(url.strip() and key.strip())

    def get_client(self) -> Client:
        """
        Returns a reusable Supabase client instance.
        Raises 503 if credentials are not configured or are placeholder values.
        """
        if not self.is_configured:
            logger.error("Supabase credentials are not configured in backend/.env")
            raise HTTPException(
                status_code=503,
                detail="Supabase credentials are not configured. Please set SUPABASE_URL and SUPABASE_KEY in backend/.env",
            )

        if self._client is None:
            try:
                logger.info("Initializing Supabase client with URL: %s", settings.supabase_url)
                self._client = create_client(settings.supabase_url.strip(), settings.supabase_key.strip())
            except Exception as e:
                logger.error("Failed to initialize Supabase client: %s", str(e))
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to connect to Supabase: {str(e)}",
                )

        return self._client


supabase_service = SupabaseService()
