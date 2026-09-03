from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SessionCreate(BaseModel):
    startup_idea: str
    target_audience: str
    industry: str
    budget: str
    timeline: str
    notes: Optional[str] = None
    status: str = "created"


class SessionUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class SessionSummary(BaseModel):
    id: str
    startup_idea: str
    target_audience: str
    industry: str
    budget: str
    timeline: str
    status: str
    created_at: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    startup_idea: str
    target_audience: str
    industry: str
    budget: str
    timeline: str
    notes: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SessionListResponse(BaseModel):
    success: bool = True
    total: int
    limit: int
    offset: int
    sessions: List[SessionSummary]
