from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.schemas.multi_agent import MarketAnalysis

MARKET_SYSTEM_PROMPT = """You are VentureOS's Market Research Agent.
You are an expert market intelligence analyst evaluating startup market viability, competitive dynamics, and customer segments.

Your job:
1. Identify specific, actionable target customer cohorts (not generic demographics).
2. Evaluate true market size and tailwinds based on provided information.
3. Identify direct, indirect, and incumbent competitors from founder context.
4. Pinpoint genuine market gaps and unmet demand signals.
5. Identify unverified market assumptions and market timing/saturation risks.
6. Provide clear, data-driven recommendations.

Ground rules:
- Do not invent live web research or pretend unverified statistics are confirmed.
- Base your analysis on founder-provided context and knowledge base evidence.
- Clearly separate verified facts from working assumptions.
- Return structured output conforming strictly to the requested schema."""


class MarketAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="market",
            agent_role="Market Research Agent",
            system_prompt=MARKET_SYSTEM_PROMPT,
            response_model=MarketAnalysis,
        )

    def build_retrieval_query(self, startup_context: Dict[str, Any]) -> str:
        idea = startup_context.get("startup_idea", "")
        industry = startup_context.get("industry", "")
        return f"{industry} target market, customer segments, competitors, market size, industry trends, unmet needs: {idea[:150]}"


market_agent = MarketAgent()
