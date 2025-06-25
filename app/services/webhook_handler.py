from fastapi import Request
from app.agents.classify_agent import classify_message
from app.models.classification_result import ClassificationResult
from app.utils.logger import logger
from datetime import datetime
from typing import Any, Dict


def normalize_webhook_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize raw webhook payload into a structured message for classification.
    Handles flexible formats from tools like Zapier, n8n, SendGrid, and Twilio.
    """
    logger.debug(f"[Webhook] Raw payload: {payload}")

    # Try to extract common fields with fallbacks
    sender = payload.get("from") or payload.get("sender") or payload.get("email") or "unknown@dsq.com"
    subject = payload.get("subject") or payload.get("title") or "(no subject)"
    content = payload.get("content") or payload.get("message") or payload.get("body") or ""
    product = payload.get("product") or payload.get("source_product") or "Unknown"
    channel = payload.get("channel") or "webhook"
    timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()

    # Optional: Try to infer product type if not given
    if product == "Unknown" and "compactor" in content.lower():
        product = "Pioneer"
    elif product == "Unknown" and "pickup" in content.lower():
        product = "Hauler"
    elif product == "Unknown" and "invoice" in content.lower():
        product = "Discovery"

    return {
        "sender": sender.strip(),
        "subject": subject.strip(),
        "content": content.strip(),
        "product": product.strip(),
        "channel": channel.strip(),
        "timestamp": timestamp
    }


async def handle_webhook(req: Request) -> ClassificationResult:
    """
    Parse and classify an incoming webhook request.

    Returns a validated ClassificationResult object.
    """
    try:
        body = await req.json()
        logger.info(f"[Webhook] Received webhook event at {datetime.utcnow().isoformat()}")

        # Normalize webhook to internal format
        normalized_msg = normalize_webhook_payload(body)

        # Run LLM-powered classification
        result_dict = classify_message(normalized_msg)

        # Enforce response schema using our Pydantic model
        result = ClassificationResult(
            **result_dict,
            classified_at=datetime.utcnow(),
            fallback_used=bool("error" in result_dict),
            error=result_dict.get("error")
        )

        logger.info(f"[Webhook] Classification complete: {result.dict()}")

        return result

    except Exception as e:
        logger.exception("[Webhook] Unhandled classification failure")
        return ClassificationResult(
            category="General Inquiry",
            priority="Medium",
            intent="Unknown",
            recommended_queue="Customer Support",
            confidence=0.0,
            classified_at=datetime.utcnow(),
            fallback_used=True,
            error=str(e)
        )
