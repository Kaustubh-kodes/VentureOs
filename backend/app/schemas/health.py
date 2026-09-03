from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: Optional[str] = "0.9.0"
    timestamp: Optional[str] = None


class RootResponse(BaseModel):
    message: str
