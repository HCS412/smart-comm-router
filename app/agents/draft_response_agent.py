import os
import openai
import json
import time
from typing import Dict, Any
from dotenv import load_dotenv
from app.agents.base_agent import BaseAgent

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class DraftResponseAgent(BaseAgent):
    """
    Agent that takes classified message data and returns a smart draft reply.
    """

    def __init__(self):
        super().__init__(name="DraftResponseAgent")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expected input:
        {
            "sender": "email@example.com",
            "content": "original message body...",
            "classification": {
                "category": "...",
                "priority": "...",
                "intent": "...",
                "recommended_queue": "...",
                "confidence": 0.87
            }
        }

        Returns:
        {
            "reply_draft": "Hello, thanks for your message...",
            "confidence": 0.92
        }
        """

        # Extract info
        content = input_data.get("content", "")
        classification = input_data.get("classification", {})

        # Prompt building
        prompt = self._build_prompt(content, classification)

        # Call LLM
        try:
            start = time.time()

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful and professional customer support assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=300
            )

            reply = response["choices"][0]["message"]["content"]
            latency = round((time.time() - start) * 1000, 2)

            return {
                "reply_draft": reply.strip(),
                "confidence": 0.92,  # You could infer this from classification.confidence
                "latency_ms": latency,
                "fallback_used": False
            }

        except Exception as e:
            return self.fallback(reason=str(e))

    def _build_prompt(self, message_content: str, classification: Dict[str, str]) -> str:
        """
        Dynamically builds a prompt for the LLM based on the message and its classification.
        """
        category = classification.get("category", "General Inquiry")
        intent = classification.get("intent", "Unclear")
        tone = self._infer_tone(category, intent)

        return f"""
You are an AI trained to write professional, polite, and helpful draft replies to incoming customer messages.

Use this classification to inform your tone and content:
- Category: {category}
- Intent: {intent}

The goal is to draft a message that:
- Is clear, courteous, and anticipatory
- Acknowledges the issue
- Reassures the user action will be taken
- Keeps the tone {tone}

--- Incoming Message ---
{message_content}
--- End Message ---

Respond ONLY with the reply message. Do not include JSON or explanation.
""".strip()

    def _infer_tone(self, category: str, intent: str) -> str:
        """
        Simple tone logic for different contexts.
        """
        if category == "Billing Support":
            return "reassuring and precise"
        if category == "Sensor Alert":
            return "calm and technically confident"
        if category == "Dispatch Communication":
            return "prompt and respectful"
        if "unsubscribe" in intent.lower():
            return "brief and compliant"
        return "neutral and helpful"
