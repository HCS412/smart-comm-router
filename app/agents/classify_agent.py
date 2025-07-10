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

class ClassificationAgent(BaseAgent):
    """
    AI agent that classifies incoming communications into actionable metadata fields:
    - category
    - intent
    - priority
    - recommended_queue
    Uses async OpenAI client, caching, and improved prompt engineering.
    """
    name: str = "ClassificationAgent"
    version: str = "2.0.0"
    fallback_config: Dict[str, Any] = {
        "category": CategoryType.GENERAL,
        "priority": PriorityLevel.MEDIUM,
        "intent": "Unknown",
        "recommended_queue": QueueType.SUPPORT,
        "confidence": 0.0
    }
    confidence_threshold: float = 0.7  # Reject classifications below this threshold

    def __init__(
        self,
        openai_client: Optional[AsyncOpenAI] = None,
        model: str = "gpt-4",
        fallback_model: str = "gpt-3.5-turbo",
        temperature: float = 0.3,
        max_tokens: int = 400
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

    def preprocess(self, input_data: AgentInput) -> None:
        if not input_data.get("content"):
            raise ValueError("Missing message content")
        if len(input_data["content"].strip()) < 10:
            raise ValueError("Content too short for meaningful classification")

    async def run(self, input_data: AgentInput) -> AgentOutput:
        content = self._sanitize(input_data["content"])
        cache_key = f"{content}:{self.model}"

        # Check cache
        if cache_key in self.cache:
            logger.info(f"[ClassificationAgent] Cache hit for: {cache_key[:50]}...")
            return self.cache[cache_key]

        prompt = self._build_prompt(content, input_data.get("metadata", {}))

        try:
            result = await self._try_classify(content, prompt, self.model)
            if result["confidence"] < self.confidence_threshold:
                logger.warning(f"[ClassificationAgent] Confidence {result['confidence']} below threshold {self.confidence_threshold}")
                raise ValueError("Classification confidence too low")
            self.cache[cache_key] = result
            return result
        except (AuthenticationError, RateLimitError, OpenAIError) as api_err:
            logger.warning(f"[ClassificationAgent] OpenAI error with {self.model}: {str(api_err)}. Falling back to {self.fallback_model}")
            try:
                result = await self._try_classify(content, prompt, self.fallback_model)
                if result["confidence"] < self.confidence_threshold:
                    raise ValueError("Fallback classification confidence too low")
                self.cache[cache_key] = result
                return result
            except Exception as e:
                logger.error(f"[ClassificationAgent] Fallback failed: {str(e)}")
                raise
        except Exception as e:
            logger.exception("[ClassificationAgent] Unexpected error")
            raise

    async def _try_classify(self, content: str, prompt: str, model: str) -> AgentOutput:
        logger.info(f"[ClassificationAgent] Sending to LLM (model: {model})")
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise customer support assistant specializing in classifying incoming communications."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            reply = response.choices[0].message.content.strip()
            return self._parse_reply(reply)
        except Exception as e:
            logger.error(f"[ClassificationAgent] LLM call failed: {str(e)}")
            raise

    def _build_prompt(self, content: str, metadata: Dict[str, Any]) -> str:
        product = metadata.get("product", "Unknown")
        return f"""
Classify the following message into a JSON object with these fields:
- category: One of [Billing Support, Dispatch Communication, Sensor Alert, Marketing, General Inquiry]
- intent: A short 1-3 word summary of the message's main intent
- priority: One of [High, Medium, Low]
- recommended_queue: One of [Finance Support, Dispatch Team, Ops Team, Automation, Customer Support]
- confidence: Float between 0.0 and 1.0 representing your certainty

Context:
- Product: {product}
- Channel: {metadata.get('channel', 'unknown')}

Few-shot examples:
1. Message: "My invoice has a double charge for last month."
   ```json
   {{
       "category": "Billing Support",
       "intent": "Invoice Dispute",
       "priority": "High",
       "recommended_queue": "Finance Support",
       "confidence": 0.95
   }}
   ```
2. Message: "When is my pickup scheduled?"
   ```json
   {{
       "category": "Dispatch Communication",
       "intent": "Schedule Inquiry",
       "priority": "Medium",
       "recommended_queue": "Dispatch Team",
       "confidence": 0.90
   }}
   ```

Message:
\"\"\"
{content}
\"\"\"
Return only the JSON object. Do not explain.
"""

    def _parse_reply(self, reply: str) -> AgentOutput:
        try:
            data = json.loads(reply) if reply.startswith('{') else {}
            result = {
                "category": data.get("category", self.fallback_config["category"]),
                "priority": data.get("priority", self.fallback_config["priority"]),
                "intent": data.get("intent", self.fallback_config["intent"]),
                "recommended_queue": data.get("recommended_queue", self.fallback_config["recommended_queue"]),
                "confidence": float(data.get("confidence", self.fallback_config["confidence"])),
                "fallback_used": False,
                "error": None
            }
            # Validate enums
            if result["category"] not in [e.value for e in CategoryType]:
                raise ValueError(f"Invalid category: {result['category']}")
            if result["priority"] not in [e.value for e in PriorityLevel]:
                raise ValueError(f"Invalid priority: {result['priority']}")
            if result["recommended_queue"] not in [e.value for e in QueueType]:
                raise ValueError(f"Invalid queue: {result['recommended_queue']}")
            return result
        except Exception as e:
            logger.warning(f"[ClassificationAgent] Failed to parse LLM reply: {reply}")
            raise ValueError(f"Invalid LLM response: {str(e)}")

    def _sanitize(self, text: str) -> str:
        clean = text.replace("\n", " ").replace("\r", "").strip()
        return clean[:2000]
