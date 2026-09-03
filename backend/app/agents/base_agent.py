import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel, ValidationError
from app.services.gemini_service import gemini_service

logger = logging.getLogger("ventureos.base_agent")


class BaseAgent(ABC):
    def __init__(
        self,
        agent_name: str,
        agent_role: str,
        system_prompt: str,
        response_model: Type[BaseModel],
    ):
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.system_prompt = system_prompt
        self.response_model = response_model

    @abstractmethod
    def build_retrieval_query(self, startup_context: Dict[str, Any]) -> str:
        """Constructs an agent-specific semantic retrieval query for pgvector."""
        pass

    def build_user_prompt(
        self,
        startup_context: Dict[str, Any],
        rag_context: Optional[str] = None,
        predecessor_context: Optional[str] = None,
    ) -> str:
        """Constructs the prompt containing startup parameters, RAG context, and predecessor agent findings."""
        idea = startup_context.get("startup_idea", "")
        audience = startup_context.get("target_audience", "")
        industry = startup_context.get("industry", "")
        budget = startup_context.get("budget", "")
        timeline = startup_context.get("timeline", "")
        notes = startup_context.get("notes") or "None provided."

        prompt_parts = [
            "--- STARTUP VENTURE PARAMETERS START ---",
            f"STARTUP IDEA:\n{idea}",
            f"TARGET AUDIENCE:\n{audience}",
            f"INDUSTRY:\n{industry}",
            f"BUDGET:\n{budget}",
            f"TIMELINE:\n{timeline}",
            f"ADDITIONAL CONTEXT:\n{notes}",
            "--- STARTUP VENTURE PARAMETERS END ---",
        ]

        if rag_context and rag_context.strip():
            prompt_parts.extend([
                "\n--- RETRIEVED FOUNDER KNOWLEDGE BASE EVIDENCE START ---",
                rag_context.strip(),
                "--- RETRIEVED FOUNDER KNOWLEDGE BASE EVIDENCE END ---",
                "EVIDENCE INSTRUCTIONS: You have access to founder-provided documents above. Use this information as supporting evidence when relevant. Ground your analysis directly in these facts.",
            ])

        if predecessor_context and predecessor_context.strip():
            prompt_parts.extend([
                "\n--- COLLABORATING AGENTS' PRIOR FINDINGS START ---",
                predecessor_context.strip(),
                "--- COLLABORATING AGENTS' PRIOR FINDINGS END ---",
                "COLLABORATION INSTRUCTIONS: Consider the prior findings from other agents above. Challenge, complement, or build upon them from your specialized perspective.",
            ])

        prompt_parts.append(
            f"\nPlease analyze this venture strictly from your perspective as the {self.agent_role}. "
            "Formulate your analysis rigorously matching the requested structured schema."
        )

        return "\n".join(prompt_parts)

    async def execute(
        self,
        startup_context: Dict[str, Any],
        rag_context: Optional[str] = None,
        predecessor_context: Optional[str] = None,
    ) -> BaseModel:
        """Executes structured reasoning via Gemini with automatic single retry on validation error."""
        user_prompt = self.build_user_prompt(startup_context, rag_context, predecessor_context)

        try:
            logger.info("Agent '%s' executing initial LLM call...", self.agent_name)
            result = await gemini_service.generate_structured(
                prompt=user_prompt,
                response_model=self.response_model,
                system_instruction=self.system_prompt,
            )
            return result
        except (ValidationError, ValueError) as err:
            logger.warning("Agent '%s' encountered validation error: %s. Initiating single retry...", self.agent_name, str(err))
            corrective_prompt = (
                f"{user_prompt}\n\n"
                f"CORRECTIVE INSTRUCTION: Your previous response failed schema validation with error: {str(err)}. "
                "Ensure every required field is present and strictly conforms to the JSON schema."
            )
            result = await gemini_service.generate_structured(
                prompt=corrective_prompt,
                response_model=self.response_model,
                system_instruction=self.system_prompt,
            )
            return result
