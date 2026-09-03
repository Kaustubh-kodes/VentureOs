from typing import Optional
from app.schemas.analysis import StartupAnalysisRequest, CEOAnalysis
from app.services.gemini_service import gemini_service

CEO_SYSTEM_PROMPT = """You are VentureOS's CEO and Strategy Agent.

You are an experienced startup strategist responsible for turning an
early-stage startup idea into an initial strategic direction.

Your job is to analyse the specific startup context provided.

Do not invent facts, competitors, market sizes or financial data.

Clearly base recommendations on the information available.

Where uncertainty exists, make reasonable assumptions internally and
provide practical recommendations rather than pretending uncertain
information is verified.

Focus on:
- Clear strategic direction
- Specific target market understanding
- Viable business model options
- Realistic revenue opportunities
- Competitive differentiation
- Actionable go-to-market strategy
- Measurable KPIs
- Realistic first 90-day execution priorities

Avoid generic startup advice.
Every recommendation should be relevant to the submitted startup idea,
target audience, industry, budget and timeline.

Be practical for an early-stage founder.
Return data strictly matching the requested structured schema."""


class CEOAgent:
    async def analyse(
        self,
        request: StartupAnalysisRequest,
        rag_context: Optional[str] = None,
    ) -> CEOAnalysis:
        notes_section = request.notes.strip() if request.notes else "None provided."

        rag_section = ""
        if rag_context and rag_context.strip():
            rag_section = f"""
--- RETRIEVED FOUNDER KNOWLEDGE BASE CONTEXT START ---
{rag_context.strip()}
--- RETRIEVED FOUNDER KNOWLEDGE BASE CONTEXT END ---

EVIDENCE GROUNDING INSTRUCTIONS:
You have access to founder-provided documents retrieved from a private knowledge base above. Use this information as supporting evidence when relevant. Ground your strategic recommendations directly in these facts. Do not invent facts that are not supported by the retrieved context. If the retrieved context does not contain enough information, state assumptions clearly.
"""

        user_prompt = f"""--- STARTUP CONTEXT START ---
STARTUP IDEA:
{request.startup_idea}

TARGET AUDIENCE:
{request.target_audience}

INDUSTRY:
{request.industry}

AVAILABLE BUDGET:
{request.budget}

TIMELINE:
{request.timeline}

ADDITIONAL NOTES:
{notes_section}
--- STARTUP CONTEXT END ---
{rag_section}
Please analyse this venture thoroughly as the CEO and Strategy Agent. Formulate the comprehensive strategic analysis strictly matching the requested structure."""

        return await gemini_service.generate_structured(
            prompt=user_prompt,
            response_model=CEOAnalysis,
            system_instruction=CEO_SYSTEM_PROMPT,
        )


ceo_agent = CEOAgent()
