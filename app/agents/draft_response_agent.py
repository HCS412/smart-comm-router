# app/agents/draft_response_agent.py

import os
import openai
import asyncio
import traceback
from typing import Dict, Any, Optional, TypedDict
from openai.error import AuthenticationError, RateLimitError, OpenAIError
from dotenv import load_dotenv
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.utils.logger import logger
from app.agents.enums import ToneStyle

load_dotenv()


class DraftResponseInput(AgentInput, total=False):
    classification: Dict[str, Any]  # Should later use TypedDict or TypedModel


class DraftResponseOutput(AgentOutput):
    reply_draft: str


class DraftResponseAgent(BaseAgent):
    """
    AI agent that generates draft replies based on classified messages.
    """

    name: str = "DraftResponseAgent"
    version: str = "1.0.0"
    fallback_config: Dict[str, Any] = {
        "reply_draft": "Thank you for your message. We are reviewing your request and will follow up shortly.",
        "confidence": 0.0
    }

    def __init__(self, openai_client: Optional[Any] = None, model: str = "gpt-4", temperature: float = 0.4, max_tokens: int = 300):
        super().__init__()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = openai_client or openai

        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY not set")

    def preprocess(self, input_data: DraftResponseInput) -> None:
        """
        Validate classification and sanitize content.
        """
        classification = input_data.get("classification", {})
        required_keys = ["category", "intent"]

        for key in required_keys:
            if key not in classification:
                raise ValueError(f"Missing classification field: {key}")

        if not input_data.get("content"):
            raise ValueError("Missing message content")

    def run(self, input_data: DraftResponseInput) -> DraftResponseOutput:
        """
        Compose a reply using the classification context and LLM prompt.
        """
        try:
            classification = input_data["classification"]
            content = self._sanitize(input_data["content"])
            tone = self._infer_tone(classification)
            prompt = self._build_prompt(content, classification, tone)

            logger.info(f"[DraftPrompt] Tone: {tone} | Intent: {classification.get('intent')}")

            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful and professional customer support assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            reply = response["choices"][0]["message"]["content"].strip()
            return {
                "reply_draft": self._process_reply(reply),
                "confidence": classification.get("confidence", 0.85),
                "fallback_used": False,
                "error": None
            }

        except (AuthenticationError, RateLimitError, OpenAIError) as api_err:
            logger.error(f"[OpenAI Error] {str(api_err)}")
            raise
        except Exception as e:
            logger.exception("[DraftAgent] Unexpected failure")
            raise

    def fallback(self, reason: str, latency: float = 0.0) -> DraftResponseOutput:
        """
        Return default reply message with error context.
        """
        return {
            "reply_draft": self.fallback_config["reply_draft"],
            "confidence": self.fallback_config["confidence"],
            "fallback_used": True,
            "error": reason,
            "_agent": self.name,
            "_version": self.version,
            "_latency_ms": latency
        }

    def _build_prompt(self, content: str, classification: Dict[str, Any], tone: str) -> str:
        return f"""
You are an AI assistant trained to write clear, empathetic, and professional email replies to incoming client messages.

Use the following classification context to shape your response:
- Category: {classification.get('category')}
- Intent: {classification.get('intent')}
- Tone: {tone}

Here is the client's original message:
"""
{content}
"""

Reply in a helpful tone. Do not include headers or disclaimers.
""".strip()

    def _infer_tone(self, classification: Dict[str, str]) -> str:
        """
        Return a tone style string based on classification.
        """
        category = classification.get("category", "General Inquiry")
        tone_map = {
            "Billing Support": "reassuring and precise",
            "Sensor Alert": "calm and technically confident",
            "Dispatch Communication": "prompt and respectful",
            "Marketing": "brief and compliant",
            "General Inquiry": "neutral and helpful"
        }
        return tone_map.get(category, "neutral and helpful")

    def _sanitize(self, text: str) -> str:
        """
        Strip problematic characters, truncate if overly long.
        """
        clean = text.replace("\n", " ").strip()
        return clean[:2000]  # soft limit

    def _process_reply(self, reply: str) -> str:
        """
        Final cleanup: ensure formatting, trim overages.
        """
        return reply.strip()[:1000]  # cap overly verbose replies
