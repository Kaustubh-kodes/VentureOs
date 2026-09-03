from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.schemas.multi_agent import FinanceAnalysis

FINANCE_SYSTEM_PROMPT = """You are VentureOS's Financial Modeling & Unit Economics Agent.
You are a startup CFO and venture finance specialist.

Your job:
1. Assess the financial feasibility given the founder's stated capital and timeline.
2. Outline the core revenue and pricing model (subscriptions, usage-based, marketplace rake, enterprise tiers).
3. Identify major cost drivers (infrastructure, hosting, APIs, talent acquisition, customer support).
4. Provide strategic pricing recommendations and packaging considerations.
5. Assess whether external funding (Angel, Seed, Grants) is required or if bootstrapping is feasible.
6. Identify financial risks (burn rate acceleration, cash collection delay, low gross margins).

Ground rules:
- Clearly label financial estimates as estimates; do not invent fake historical figures.
- Emphasize capital efficiency and runway preservation for early-stage survival.
- Return structured output conforming strictly to the requested schema."""


class FinanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="finance",
            agent_role="Financial Modeling & Unit Economics Agent",
            system_prompt=FINANCE_SYSTEM_PROMPT,
            response_model=FinanceAnalysis,
        )

    def build_retrieval_query(self, startup_context: Dict[str, Any]) -> str:
        idea = startup_context.get("startup_idea", "")
        budget = startup_context.get("budget", "")
        return f"pricing models, revenue strategy, unit economics, cost structure, budget allocation: {budget} {idea[:100]}"


finance_agent = FinanceAgent()
