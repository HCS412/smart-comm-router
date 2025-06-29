import os
import openai
import traceback
from typing import Dict, Any, Optional
from openai.error import AuthenticationError, RateLimitError, OpenAIError
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
    """

    name: str = "ClassificationAgent"
    version: str = "1.0.0"
    fallback_config: Dict[str, Any] = {
        "category": CategoryType.GENERAL,
        "priority": PriorityLevel.MEDIUM,
        "intent": "Unknown",
        "recommended_queue": QueueType.SUPPORT,
        "confidence": 0.0
    }

    def __init__(self, openai_client: Optional[Any] = None, model: str = "gpt-4", temperature: float = 0.3, max_tokens: int = 400):
        super().__init__()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = openai_client or openai

        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY not set")

    def preprocess(self, input_data: AgentInput) -> None:
        if not input_data.get("content"):
            raise ValueError("Missing message content")

    def run(self, input_data: AgentInput) -> AgentOutput:
        try:
            content = self._sanitize(input_data["content"])
            prompt = self._build_prompt(content)

            logger.info(f"[Classification] Prompt ready, sending to LLM")

            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a customer support assistant that classifies incoming emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            reply = response["choices"][0]["message"]["content"].strip()
            return self._parse_reply(reply)

        except (AuthenticationError, RateLimitError, OpenAIError) as api_err:
            logger.error(f"[OpenAI Error] {str(api_err)}")
            raise
        except Exception as e:
            logger.exception("[ClassificationAgent] Unexpected error")
            raise

    def _build_prompt(self, content: str) -> str:
        return f"""
Classify the following message by returning a JSON object with these fields:
- category: One of [Billing Support, Dispatch Communication, Sensor Alert, Marketing, General Inquiry]
- intent: A short 1-3 word summary of the message's main intent
- priority: One of [High, Medium, Low]
- recommended_queue: One of [Finance Support, Dispatch Team, Ops Team, Automation, Customer Support]
- confidence: Float between 0.0 and 1.0 representing your certainty

Message:
"""
{content}
"""
Return only the JSON. Do not explain."
        
    def _parse_reply(self, reply: str) -> AgentOutput:
        try:
            data = eval(reply) if reply.startswith('{') else {}
            return {
                "category": data.get("category", self.fallback_config["category"]),
                "priority": data.get("priority", self.fallback_config["priority"]),
                "intent": data.get("intent", self.fallback_config["intent"]),
                "recommended_queue": data.get("recommended_queue", self.fallback_config["recommended_queue"]),
                "confidence": float(data.get("confidence", self.fallback_config["confidence"])),
                "fallback_used": False,
                "error": None
            }
        except Exception as e:
            logger.warning(f"[ClassificationAgent] Failed to parse LLM reply: {reply}")
            raise

    def _sanitize(self, text: str) -> str:
        return text.replace("\n", " ").strip()[:2000]
