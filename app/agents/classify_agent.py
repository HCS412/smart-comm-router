import os
import openai
import json
from dotenv import load_dotenv
from app.utils.logger import logger

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- 1. Prompt Construction ----------
def build_prompt(msg: dict) -> str:
    """
    Build a detailed, structured prompt for DSQ’s AI message triage system.
    """
    subject = msg.get("subject", "(no subject)")
    product = msg.get("product", "Unknown")
    content = msg.get("content", "")
    sender = msg.get("sender", "Unknown")

    return f"""
You are an AI assistant working for **DSQ Technology**, which manages:
- Discovery: automated invoice auditing & billing support
- Hauler: roll-off dispatch scheduling, ETA coordination
- Pioneer: compactor sensors and monitoring alerts

Given a message, your job is to return a structured classification object with:
- "category": What type of issue this is (e.g. 'Billing', 'Dispatch', 'Sensor Alert')
- "priority": High, Medium, or Low
- "intent": Specific problem or user goal (e.g. 'Invoice Dispute', 'Pickup ETA')
- "recommended_queue": Which team should handle this (e.g. 'Finance', 'Dispatch')
- "confidence": float between 0.0 and 1.0 based on how certain you are

You MUST respond with valid JSON. Do not include any extra commentary or text.

--- EXAMPLE FORMAT ---
{{
  "category": "Billing",
  "priority": "High",
  "intent": "Duplicate Invoice",
  "recommended_queue": "Finance",
  "confidence": 0.94
}}

--- MESSAGE INPUT START ---
Sender: {sender}
Product: {product}
Subject: {subject}
Content:
{content}
--- MESSAGE INPUT END ---
""".strip()

# ---------- 2. Safe Response Parsing ----------
def parse_response(reply: str) -> dict:
    """
    Safely parse the LLM's response into a Python dict.
    """
    try:
        start = reply.find("{")
        end = reply.rfind("}") + 1
        json_str = reply[start:end]
        parsed = json.loads(json_str)

        required_keys = {"category", "priority", "intent", "recommended_queue", "confidence"}
        if not required_keys.issubset(parsed.keys()):
            raise ValueError("Missing required keys in response")

        return parsed
    except Exception as e:
        logger.error(f"[LLM Parse Error] Raw response: {reply}")
        raise RuntimeError(f"Failed to parse LLM response: {e}")

# ---------- 3. LLM Classification Orchestration ----------
def classify_message(msg: dict) -> dict:
    """
    Classify a message using OpenAI GPT-4 with structured JSON output.
    """
    prompt = build_prompt(msg)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI triage assistant for DSQ Technology."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        reply = response['choices'][0]['message']['content']
        result = parse_response(reply)

        logger.info(f"[LLM Classification] Result: {result}")
        return result

    except Exception as e:
        logger.exception("LLM classification failed. Falling back to default classification.")
        return {
            "category": "General Inquiry",
            "priority": "Medium",
            "intent": "Unclear",
            "recommended_queue": "Customer Support",
            "confidence": 0.5,
            "error": str(e)
        }
