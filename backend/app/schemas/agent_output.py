from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.schemas.session import SessionResponse


class AgentOutputCreate(BaseModel):
    session_id: str
    agent_name: str
    status: str = "pending"
    output_json: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AgentOutputUpdate(BaseModel):
    status: Optional[str] = None
    output_json: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AgentOutputResponse(BaseModel):
    id: Optional[str] = None
    session_id: str
    agent_name: str
    status: str
    output: Optional[Dict[str, Any]] = Field(default=None, alias="output_json")
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        populate_by_name = True


class SessionDetailsResponse(BaseModel):
    success: bool = True
    session: SessionResponse
    agent_outputs: List[AgentOutputResponse]
