from fastapi import Request, HTTPException
from app.agents.classify_agent import ClassificationAgent
from app.models.classification_result import ClassificationResult
from app.utils.logger import logger
from datetime import datetime
from typing import Any, Dict

async def normalize_webhook_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes raw webhook payload into a structured message for classification.
    Handles mock formats simulating Gmail, Twilio, and generic webhook sources.
    
    Args:
        payload: Raw webhook payload (e.g., from n8n, Zapier, Gmail, Twilio).
    
    Returns:
        Dict[str, Any]: Normalized message with sender, subject, content, product, channel, and metadata.
    
    Raises:
        ValueError: If critical fields (sender, content) are missing or invalid.
    """
    logger.debug(f"[Webhook] Normalizing payload: {payload}")
    
    # Determine source type
    channel = payload.get("channel", "webhook").lower()
    
    # Normalize based on source
    if channel == "gmail":
        sender = payload.get("from") or payload.get("sender") or payload.get("email") or None
        subject = payload.get("subject") or payload.get("title") or "(no subject)"
        content = payload.get("message") or payload.get("content") or payload.get("body") or ""
        metadata = {
            "thread_id": payload.get("thread_id", "mock-thread-123"),
            "labels": payload.get("labels", ["INBOX", "UNREAD"]),
            "timestamp": payload.get("timestamp", datetime.utcnow().isoformat())
        }
    elif channel == "phone":
        sender = payload.get("From") or payload.get("sender") or None
        subject = "(no subject)"
        content = payload.get("TranscriptionText") or payload.get("content") or ""
        metadata = {
            "call_sid": payload.get("CallSid", "mock-call-sid-456"),
            "transcription_confidence": float(payload.get("TranscriptionConfidence", 0.92)),
            "timestamp": payload.get("timestamp", datetime.utcnow().isoformat())
        }
    else:
        sender = payload.get("from") or payload.get("sender") or payload.get("email") or None
        subject = payload.get("subject") or payload.get("title") or "(no subject)"
        content = payload.get("message") or payload.get("content") or payload.get("body") or ""
        metadata = payload.get("metadata", {})
    
    # Infer product if not provided
    product = payload.get("product") or payload.get("source_product") or "Unknown"
    if product == "Unknown":
        content_lower = content.lower()
        if "compactor" in content_lower:
            product = "Pioneer"
        elif "pickup" in content_lower:
            product = "Hauler"
        elif "invoice" in content_lower:
            product = "Discovery"
    
    # Validate required fields
    if not sender:
        logger.error("[Webhook] Missing sender in payload")
        raise ValueError("Missing required field: sender")
    if not content:
        logger.error("[Webhook] Missing content in payload")
        raise ValueError("Missing required field: content")
    
    normalized = {
        "sender": sender.strip(),
        "subject": subject.strip(),
        "content": content.strip(),
        "product": product.strip(),
        "channel": channel.strip(),
        "timestamp": metadata.get("timestamp", datetime.utcnow().isoformat()),
        "metadata": metadata
    }
    
    logger.info(f"[Webhook] Normalized payload: {normalized}")
    return normalized

async def handle_webhook(req: Request) -> ClassificationResult:
    """
    Parses and classifies an incoming webhook request (mock implementation).
    
    Args:
        req: FastAPI Request object containing the webhook payload.
    
    Returns:
        ClassificationResult: Validated classification result.
    
    Raises:
        HTTPException: For invalid payloads or classification failures.
    """
    try:
        body = await req.json()
        logger.info(f"[Webhook] Received webhook event at {datetime.utcnow().isoformat()}")
        
        # Normalize webhook to internal format
        normalized_msg = await normalize_webhook_payload(body)
        
        # Run LLM-powered classification
        classify_agent = ClassificationAgent()
        classify_agent.set_metadata({
            "request_id": getattr(req.state, "request_id", "unknown"),
            "ip": req.client.host
        })
        result_dict = await classify_agent.execute(normalized_msg)
        
        # Enforce response schema
        result = ClassificationResult(
            **result_dict,
            classified_at=datetime.utcnow(),
            fallback_used=bool(result_dict.get("error")),
            error=result_dict.get("error")
        )
        
        logger.info(f"[Webhook] Classification complete: {result.dict()}")
        return result
    except ValueError as ve:
        logger.error("[Webhook] Invalid payload: %s", str(ve))
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(ve)}")
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
