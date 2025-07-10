import os
import json
import asyncio
from typing import Dict, Any, Optional
from cachetools import TTLCache
from openai import AsyncOpenAI, OpenAIError, AuthenticationError, RateLimitError
from dotenv import load_dotenv
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.utils.logger import logger
from app.agents.enums import PriorityLevel, CategoryType, QueueType

load_dotenv()

class DraftResponseInput(AgentInput, total=False):
    classification: Dict[str, Any]

class DraftResponseOutput(AgentOutput):
    reply_draft: str

class DraftResponseAgent(BaseAgent):
    """
    AI agent that generates draft responses for classified messages.
    Uses async OpenAI client, caching, and dynamic tone based on classification.
    """
    name: str = "DraftResponseAgent"
    version: str = "2.0.0"
    fallback_config: Dict[str, Any] = {
        "reply_draft": "Thank you for your message. We are reviewing your request and will follow up shortly.",
        "category": CategoryType.GENERAL,
        "priority": PriorityLevel.MEDIUM,
        "intent": "Unknown",
        "recommended_queue": QueueType.SUPPORT,
        "confidence": 0.0
    }
    confidence_threshold: float = 0.7

    def __init__(
        self,
        openai_client: Optional[AsyncOpenAI] = None,
        model: str = "gpt-4",
        fallback_model: str = "gpt-3.5-turbo",
        temperature: float = 0.4,
        max_tokens: int = 300
    ):
        super().__init__()
        self.model = model
        self.fallback_model = fallback_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = openai_client or AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cache = TTLCache(maxsize=1000, ttl=3600)  # Cache for 1 hour

        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY not set")

    def preprocess(self, input_data: DraftResponseInput) -> None:
        classification = input_data.get("classification", {})
        required_keys = ["category", "intent"]
        for key in required_keys:
            if key not in classification:
                raise ValueError(f"Missing classification field: {key}")
        if not input_data.get("content"):
            raise ValueError("Missing message content")
        if len(input_data["content"].strip()) < 10:
            raise ValueError("Content too short for meaningful response")

    async def run(self, input_data: DraftResponseInput) -> DraftResponseOutput:
        classification = input_data["classification"]
        content = self._sanitize(input_data["content"])
        cache_key = f"{content}:{classification.get('category')}:{classification.get('intent')}:{self.model}"

        # Check cache
        if cache_key in self.cache:
            logger.info(f"[DraftResponseAgent] Cache hit for: {cache_key[:50]}...")
            return self.cache[cache_key]

        tone = self._infer_tone(classification)
        prompt = self._build_prompt(content, classification, tone)

        try:
            result = await self._try_draft(content, prompt, classification, self.model)
            if result["confidence"] < self.confidence_threshold:
                logger.warning(f"[DraftResponseAgent] Confidence {result['confidence']} below threshold {self.confidence_threshold}")
                raise ValueError("Draft confidence too low")
            self.cache[cache_key] = result
            return result
        except (AuthenticationError, RateLimitError, OpenAIError) as api_err:
            logger.warning(f"[DraftResponseAgent] OpenAI error with {self.model}: {str(api_err)}. Falling back to {self.fallback_model}")
            try:
                result = await self._try_draft(content, prompt, classification, self.fallback_model)
                if result["confidence"] < self.confidence_threshold:
                    raise ValueError("Fallback draft confidence too low")
                self.cache[cache_key] = result
                return result
            except Exception as e:
                logger.error(f"[DraftResponseAgent] Fallback failed: {str(e)}")
                raise
        except Exception as e:
            logger.exception("[DraftResponseAgent] Unexpected error")
            raise

    async def _try_draft(self, content: str, prompt: str, classification: Dict[str, Any], model: str) -> DraftResponseOutput:
        logger.info(f"[DraftResponseAgent] Generating draft with model: {model}")
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional customer support assistant crafting clear, empathetic, and concise email replies."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            reply = response.choices[0].message.content.strip()
            output: DraftResponseOutput = {
                "reply_draft": self._process_reply(reply),
                "confidence": classification.get("confidence", 0.85),
                "fallback_used": False,
                "error": None,
                "category": classification.get("category", self.fallback_config["category"]),
                "priority": classification.get("priority", self.fallback_config["priority"]),
                "intent": classification.get("intent", self.fallback_config["intent"]),
                "recommended_queue": classification.get("recommended_queue", self.fallback_config["recommended_queue"])
            }
            return output
        except Exception as e:
            logger.error(f"[DraftResponseAgent] LLM call failed: {str(e)}")
            raise

    def _build_prompt(self, content: str, classification: Dict[str, Any], tone: str) -> str:
        product = classification.get("metadata", {}).get("product", "Unknown")
        return f"""
You are an AI assistant trained to write clear, empathetic, and professional email replies for customer support.

Context:
- Category: {classification.get('category')}
- Intent: {classification.get('intent')}
- Tone: {tone}
- Product: {product}

Few-shot examples:
1. Category: Billing Support, Intent: Invoice Dispute, Tone: reassuring and precise
   Message: "My invoice has a double charge for last month."
   Reply: "Thank you for bringing this to our attention. We apologize for the inconvenience. Our finance team is reviewing your invoice and will resolve the double charge promptly. You'll hear back within 24 hours."
2. Category: Dispatch Communication, Intent: Schedule Inquiry, Tone: prompt and respectful
   Message: "When is my pickup scheduled?"
   Reply: "Thank you for reaching out. Your pickup is scheduled for [insert date/time]. Our dispatch team will confirm 24 hours prior. Please let us know if you need to adjust the schedule."

Client's message:
\"\"\"
{content}
\"\"\"
Craft a concise reply (100-150 words) in the specified tone. Do not include headers, disclaimers, or signatures. Return only the response text.
"""

    def _infer_tone(self, classification: Dict[str, str]) -> str:
        category = classification.get("category", CategoryType.GENERAL)
        tone_map = {
            CategoryType.BILLING: "reassuring and precise",
            CategoryType.SENSOR: "calm and technically confident",
            CategoryType.DISPATCH: "prompt and respectful",
            CategoryType.MARKETING: "brief and compliant",
            CategoryType.GENERAL: "neutral and helpful"
        }
        return tone_map.get(category, "neutral and helpful")

    def _sanitize(self, text: str) -> str:
        clean = text.replace("\n", " ").replace("\r", "").strip()
        return clean[:2000]

    def _process_reply(self, reply: str) -> str:
        clean_reply = reply.strip()[:1000]
        # Ensure reply ends with a period
        if clean_reply and not clean_reply.endswith("."):
            clean_reply += "."
        return clean_reply
