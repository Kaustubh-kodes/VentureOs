from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ---------------------------------------------------------------------------
# Specialized Agent Output Models
# ---------------------------------------------------------------------------

class SourceReference(BaseModel):
    document_id: Optional[str] = None
    document_name: str
    chunk_id: Optional[str] = None
    page: Optional[int] = None
    similarity_score: Optional[float] = None


class MarketAnalysis(BaseModel):
    agent: str = "market"
    market_summary: str = Field(description="Executive summary of the market opportunity and dynamics")
    target_customers: List[str] = Field(description="Specific target customer segments and buyer profiles")
    market_opportunity: str = Field(description="Total addressable market and market tailwinds assessment")
    competitive_landscape: List[str] = Field(description="Direct, indirect, and incumbent competitors")
    market_gaps: List[str] = Field(description="Unmet needs and opportunities in the current market")
    key_assumptions: List[str] = Field(description="Critical market assumptions that must be validated")
    risks: List[str] = Field(description="Market risks including timing, saturation, and customer inertia")
    recommendations: List[str] = Field(description="Actionable market research priorities for founders")
    confidence: int = Field(ge=0, le=100, description="Confidence score in market viability (0-100)")
    sources_used: List[SourceReference] = Field(default_factory=list)


class ProductAnalysis(BaseModel):
    agent: str = "product"
    product_summary: str = Field(description="Product vision and architectural summary")
    core_value_proposition: str = Field(description="Primary value proposition delivered to the end user")
    primary_user_problem: str = Field(description="Core friction point solved by this product")
    mvp_features: List[str] = Field(description="Strict must-have features required for initial launch")
    future_features: List[str] = Field(description="Nice-to-have features reserved for subsequent iterations")
    differentiators: List[str] = Field(description="Technical or functional moats separating this product")
    product_risks: List[str] = Field(description="Technical feasibility, complexity, and adoption risks")
    validation_steps: List[str] = Field(description="Hypothesis tests to validate product-market fit")
    recommendations: List[str] = Field(description="Pragmatic engineering and UX recommendations")
    sources_used: List[SourceReference] = Field(default_factory=list)


class MarketingAnalysis(BaseModel):
    agent: str = "marketing"
    positioning: str = Field(description="Unique brand and market positioning statement")
    target_personas: List[str] = Field(description="Detailed user and buyer personas with pain points")
    key_message: str = Field(description="Core brand messaging and value headline")
    recommended_channels: List[str] = Field(description="High-ROI customer acquisition channels tailored to budget")
    gtm_strategy: List[str] = Field(description="Sequential go-to-market rollout steps")
    experiments: List[str] = Field(description="Low-cost growth and acquisition experiments to run first")
    growth_risks: List[str] = Field(description="CAC inflation, platform dependency, and conversion bottlenecks")
    recommendations: List[str] = Field(description="Immediate marketing action items")
    sources_used: List[SourceReference] = Field(default_factory=list)


class FinanceAnalysis(BaseModel):
    agent: str = "finance"
    financial_summary: str = Field(description="High-level financial health and runway evaluation")
    revenue_model: str = Field(description="Pricing mechanism, tiers, and unit economics structure")
    major_cost_areas: List[str] = Field(description="Primary operational, hosting, and human capital expenses")
    pricing_considerations: List[str] = Field(description="Recommended pricing levels, packaging, and discounting rules")
    funding_assessment: str = Field(description="Capital efficiency assessment and external funding requirements")
    financial_risks: List[str] = Field(description="Cash burn, working capital, and margin compression risks")
    key_assumptions: List[str] = Field(description="Financial hypotheses requiring sensitivity analysis")
    recommendations: List[str] = Field(description="Budget allocation and milestone targets")
    sources_used: List[SourceReference] = Field(default_factory=list)


class InvestmentAnalysis(BaseModel):
    agent: str = "investment"
    investment_summary: str = Field(description="Venture capitalist evaluation of investment readiness")
    investment_score: int = Field(ge=0, le=100, description="Overall venture investment score (0-100)")
    strengths: List[str] = Field(description="Compelling reasons an investor would back this startup")
    major_risks: List[str] = Field(description="Top existential risks threatening business viability")
    critical_assumptions: List[str] = Field(description="Unverified premises where failure breaks the thesis")
    red_flags: List[str] = Field(description="Issues that would trigger an immediate pass from investors")
    investment_readiness: str = Field(description="Readiness stage: Pre-Seed, Seed, Series A, or Not Ready")
    conditions_for_investment: List[str] = Field(description="Milestones founders must prove before pitching")
    recommendations: List[str] = Field(description="Tough-love recommendations to derisk the venture")
    sources_used: List[SourceReference] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Contradiction & Final Synthesis Report
# ---------------------------------------------------------------------------

class ConflictingAssessment(BaseModel):
    area: str = Field(description="Topic area of disagreement (e.g. Market Size, Pricing, Feasibility)")
    agent_a: str = Field(description="First agent name")
    agent_a_view: str = Field(description="First agent's perspective")
    agent_b: str = Field(description="Second agent name")
    agent_b_view: str = Field(description="Second agent's contrasting perspective")
    analysis: str = Field(description="Why this conflict exists and what the founder must test")


class SynthesisReport(BaseModel):
    agent: str = "synthesis"
    executive_summary: str = Field(description="High-level investor-ready executive summary")
    startup_overview: str = Field(description="Venture snapshot and foundational identity")
    problem: str = Field(description="Comprehensive definition of the pain point")
    solution: str = Field(description="Product solution and value realization")
    target_customers: List[str] = Field(description="Primary, secondary, and tertiary customer cohorts")
    market_opportunity: str = Field(description="Macro market size and expansion avenues")
    competitive_position: str = Field(description="Defensible moat and competitive dynamics")
    product_strategy: str = Field(description="Product roadmap and technological feasibility")
    mvp_recommendation: str = Field(description="Minimum viable scope and release guardrails")
    gtm_strategy: str = Field(description="Omnichannel customer acquisition blueprint")
    business_model: str = Field(description="Monetization mechanics and customer lifetime value drivers")
    financial_assessment: str = Field(description="Unit economics, burn rate trajectory, and break-even factors")
    key_risks: List[str] = Field(description="Top consolidated organizational, market, and technical risks")
    critical_assumptions: List[str] = Field(description="Foundational hypotheses that must be validated")
    investment_readiness: str = Field(description="Overall fundraising readiness stage")
    investment_score: int = Field(ge=0, le=100, description="Calibrated venture score (0-100)")
    top_5_priorities: List[str] = Field(description="The 5 most urgent actions for the founding team")
    action_plan_30_days: List[str] = Field(description="Week 1-4 execution milestones")
    action_plan_90_days: List[str] = Field(description="Month 2-3 validation and traction milestones")
    final_verdict: str = Field(description="Final strategic verdict: Pursue, Pivot, or Halt")
    conflicting_assessments: List[ConflictingAssessment] = Field(
        default_factory=list,
        description="Explicitly surfaced disagreements between specialized agents"
    )
    sources_used: List[SourceReference] = Field(
        default_factory=list,
        description="Aggregated knowledge base sources used across all agents"
    )


# ---------------------------------------------------------------------------
# API Progress & Logging Models
# ---------------------------------------------------------------------------

class AgentExecutionLog(BaseModel):
    id: Optional[str] = None
    session_id: str
    agent_name: str
    event_type: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None


class AnalysisEventItem(BaseModel):
    id: Optional[str] = None
    timestamp: str
    agent_name: str
    event_type: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalysisEventsResponse(BaseModel):
    success: bool = True
    session_id: str
    events: List[AnalysisEventItem]


class AgentStatusInfo(BaseModel):
    name: str
    display_name: str
    status: str = "pending"  # pending, retrieving, analysing, completed, failed
    sources_count: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None


class MultiAgentStatusResponse(BaseModel):
    success: bool = True
    session_id: str
    overall_status: str
    session_status: str  # Backwards compatibility
    progress_percentage: int = 0
    overall_progress: int = 0  # Backwards compatibility
    current_agent: Optional[str] = None
    started_at: Optional[str] = None
    updated_at: Optional[str] = None
    agents: List[AgentStatusInfo]
    agents_map: Dict[str, AgentStatusInfo] = Field(default_factory=dict)
    has_final_report: bool = False
    events_count: int = 0
    logs_count: int = 0  # Backwards compatibility


class MultiAgentRunResponse(BaseModel):
    success: bool = True
    session_id: str
    message: str = "Multi-agent intelligence analysis initiated"


class AnalysisHistoryItem(BaseModel):
    id: str
    startup_idea: str
    industry: str
    target_audience: str
    budget: str
    timeline: str
    status: str
    investment_score: Optional[int] = None
    investment_readiness: Optional[str] = None
    sources_count: int = 0
    created_at: Optional[str] = None


class PaginatedAnalysisHistoryResponse(BaseModel):
    success: bool = True
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[AnalysisHistoryItem]
