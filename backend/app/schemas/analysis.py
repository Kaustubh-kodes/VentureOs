from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class StartupAnalysisRequest(BaseModel):
    startup_idea: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Core startup idea description (10-2000 chars)"
    )
    target_audience: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Target customer or audience segment"
    )
    industry: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Target industry sector"
    )
    budget: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Available starting budget tier"
    )
    timeline: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Target launch or execution timeline"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional additional founder notes or constraints"
    )


class CEOAnalysis(BaseModel):
    vision_statement: str = Field(description="Inspiring long-term vision statement for the venture")
    mission_statement: str = Field(description="Clear and purposeful mission statement")
    problem_definition: str = Field(description="Precise definition of the pain point being solved")
    business_model: str = Field(description="Core operating and value delivery model")
    revenue_streams: List[str] = Field(description="List of realistic monetization channels")
    competitive_advantage: str = Field(description="Defensible moat and key differentiators")
    target_market_description: str = Field(description="Detailed profile of ideal early adopter market")
    key_performance_indicators: List[str] = Field(description="Top quantifiable KPIs to monitor")
    success_metrics: List[str] = Field(description="Milestones indicating product-market traction")
    go_to_market_summary: str = Field(description="Initial GTM strategy and customer acquisition summary")
    founding_team_requirements: List[str] = Field(description="Essential initial roles or skill sets needed")
    first_90_days_priorities: List[str] = Field(description="Ranked execution priorities for the first 90 days")


class CEOAnalysisResponse(BaseModel):
    success: bool = True
    session_id: Optional[str] = Field(default=None, description="Persistent UUID of the startup session")
    status: str = Field(default="completed", description="Execution status")
    sources_used: List[Dict[str, Any]] = Field(default_factory=list, description="Knowledge base sources used for grounding")
    data: CEOAnalysis
