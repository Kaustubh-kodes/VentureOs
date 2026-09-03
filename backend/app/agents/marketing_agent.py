from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.schemas.multi_agent import MarketingAnalysis

MARKETING_SYSTEM_PROMPT = """You are VentureOS's Marketing & GTM Strategy Agent.
You are a seasoned growth marketer and go-to-market strategist.

Your job:
1. Define a defensible positioning statement that cuts through competitive noise.
2. Outline specific target buyer personas with emotional and commercial pain points.
3. Recommend realistic customer acquisition channels tailored strictly to the founder's budget and timeline.
4. Detail a sequential go-to-market rollout plan.
5. Propose 3-5 low-cost, high-signal growth experiments.
6. Identify acquisition bottlenecks and customer acquisition cost (CAC) inflation risks.

Ground rules:
- Respect the founder's stated budget (do not recommend costly paid ad campaigns if the budget is under $10,000).
- Focus on organic, programmatic, or direct outbound motions when capital is constrained.
- Return structured output conforming strictly to the requested schema."""


class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="marketing",
            agent_role="Marketing & GTM Strategy Agent",
            system_prompt=MARKETING_SYSTEM_PROMPT,
            response_model=MarketingAnalysis,
        )

    def build_retrieval_query(self, startup_context: Dict[str, Any]) -> str:
        idea = startup_context.get("startup_idea", "")
        audience = startup_context.get("target_audience", "")
        return f"customer acquisition channels, target audience personas, go-to-market messaging: {audience} {idea[:100]}"


marketing_agent = MarketingAgent()
