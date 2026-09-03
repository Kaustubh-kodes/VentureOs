import asyncio
import json
import logging
import re
from typing import Type, TypeVar, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger("ventureos.services.gemini")

T = TypeVar("T", bound=BaseModel)


class GeminiService:
    def __init__(self):
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            api_key = settings.gemini_api_key
            if not api_key:
                logger.error("GEMINI_API_KEY is not set.")
                raise HTTPException(
                    status_code=500,
                    detail="AI service is not configured. Missing GEMINI_API_KEY.",
                )
            self._client = genai.Client(api_key=api_key)
        return self._client

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
    ) -> T:
        """
        Reusable structured generation using the official Google Gen AI SDK.
        Guarantees validation against the supplied Pydantic response_model.
        Includes:
        - Configurable timeout (default 60s)
        - Automatic 429 exponential backoff
        - Fallback candidate model (gemini-3.5-flash-lite)
        - 1-attempt controlled JSON repair flow for malformed outputs (Phase 8/9 Part 14)
        """
        client = self._get_client()
        target_model = model or settings.gemini_model or "gemini-3.5-flash"

        candidate_models = [target_model]
        if target_model != "gemini-3.5-flash-lite":
            candidate_models.append("gemini-3.5-flash-lite")

        response = None
        last_exception = None
        timeout = settings.llm_timeout_seconds

        for curr_model in candidate_models:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_model,
                system_instruction=system_instruction,
                temperature=0.2,
            )

            for attempt in range(settings.llm_max_retries):
                try:
                    logger.info("Calling Gemini API with model: %s (attempt %d, timeout %ds)", curr_model, attempt + 1, timeout)
                    response = await asyncio.wait_for(
                        client.aio.models.generate_content(
                            model=curr_model,
                            contents=prompt,
                            config=config,
                        ),
                        timeout=timeout,
                    )
                    break
                except asyncio.TimeoutError:
                    logger.warning("Gemini call timed out after %ds on %s (attempt %d)", timeout, curr_model, attempt + 1)
                    last_exception = TimeoutError(f"LLM call exceeded {timeout}s timeout")
                    continue
                except APIError as e:
                    last_exception = e
                    err_str = str(e)
                    logger.warning("Gemini API error on model %s: %s", curr_model, err_str[:120])
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        delay = min(4 * (attempt + 1), 12)
                        match = re.search(r"retry in (\d+)", err_str)
                        if match:
                            delay = min(int(match.group(1)), 12)
                        logger.info("Rate limit hit, pausing %ds before retry...", delay)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        break
                except Exception as e:
                    last_exception = e
                    logger.error("Unexpected error on model %s: %s", curr_model, str(e))
                    break

            if response is not None:
                break

        if response is None:
            if isinstance(last_exception, APIError):
                msg = getattr(last_exception, "message", str(last_exception))
                raise HTTPException(status_code=503, detail=f"Gemini service error: {msg}")
            if isinstance(last_exception, TimeoutError):
                raise HTTPException(status_code=504, detail="AI service timed out while generating analysis.")
            raise HTTPException(
                status_code=500,
                detail="AI service failed to respond after candidate model fallbacks.",
            )

        # Parse and validate response
        raw_text = getattr(response, "text", "") or ""
        try:
            if hasattr(response, "parsed") and isinstance(response.parsed, response_model):
                return response.parsed

            clean_text = self._clean_json_text(raw_text)
            return response_model.model_validate_json(clean_text)
        except (ValidationError, json.JSONDecodeError) as initial_err:
            logger.warning(
                "Initial schema validation failed for %s: %s. Initiating 1 controlled repair attempt...",
                response_model.__name__,
                str(initial_err)[:150],
            )
            # PART 14: One controlled repair attempt
            try:
                repair_prompt = (
                    f"The previous output had a JSON validation error against schema {response_model.__name__}:\n"
                    f"Error: {str(initial_err)[:200]}\n\n"
                    f"Original raw text:\n{raw_text[:1200]}\n\n"
                    f"Fix the JSON structure. Return ONLY valid JSON matching the schema."
                )
                repair_response = await asyncio.wait_for(
                    client.aio.models.generate_content(
                        model=curr_model,
                        contents=repair_prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=response_model,
                            temperature=0.1,
                        ),
                    ),
                    timeout=30,
                )
                if hasattr(repair_response, "parsed") and isinstance(repair_response.parsed, response_model):
                    logger.info("Controlled repair successful for %s", response_model.__name__)
                    return repair_response.parsed

                repaired_text = self._clean_json_text(getattr(repair_response, "text", "") or "")
                repaired_obj = response_model.model_validate_json(repaired_text)
                logger.info("Controlled repair validation successful for %s", response_model.__name__)
                return repaired_obj
            except Exception as repair_err:
                logger.error("Controlled repair attempt failed for %s: %s", response_model.__name__, str(repair_err))
                raise HTTPException(
                    status_code=500,
                    detail=f"Model output failed validation for {response_model.__name__} after repair attempt.",
                )

    def _clean_json_text(self, text: str) -> str:
        raw = text.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        return raw.strip()


gemini_service = GeminiService()
