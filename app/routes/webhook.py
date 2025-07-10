from fastapi import APIRouter, Request, Header, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.webhook_handler import handle_webhook
from app.models.classification_result import ClassificationResult
from app.utils.logger import logger
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

@router.post(
    "/incoming",
    response_model=ClassificationResult,
    summary="Process incoming webhook payload",
    response_description="Structured classification of the message"
)
async def webhook_entrypoint(
    req: Request,
    x_api_key: Optional[str] = Header(None, description="Optional API key for webhook security")
):
    """
    Accepts an inbound message payload from external services (e.g., n8n, Zapier, email parser, Twilio).
    Normalizes and classifies it using LLMs, returning a validated structured response.
    
    Headers:
        - X-API-Key: Optional token-based protection (mock validation in prototype)
    
    Payload Examples:
        Gmail:
        ```json
        {
            "from": "client@example.com",
            "subject": "Roll-off ETA missing",
            "message": "Hi, we scheduled a pickup but haven’t received an ETA.",
            "channel": "gmail",
            "product": "Hauler",
            "thread_id": "mock-thread-123",
            "labels": ["INBOX", "UNREAD"],
            "timestamp": "2025-07-10T12:00:00Z"
        }
        ```
        Twilio:
        ```json
        {
            "From": "+15551234567",
            "TranscriptionText": "I need to reschedule my pickup.",
            "channel": "phone",
            "product": "Hauler",
            "CallSid": "mock-call-sid-456",
            "TranscriptionConfidence": 0.92,
            "timestamp": "2025-07-10T12:00:00Z"
        }
        ```
    
    Returns:
        ClassificationResult: Structured classification with category, intent, priority, and queue.
    
    Raises:
        HTTPException: For invalid API keys or processing failures.
    """
    try:
        logger.info(f"[Webhook] Request received at {datetime.utcnow().isoformat()} | IP: {req.client.host}")
        
        # Mock API key validation (for demonstration)
        if x_api_key and x_api_key != "mock-api-key-123":
            logger.warning("[Webhook] Invalid API key provided")
            raise HTTPException(status_code=403, detail="Invalid API key")
        
        classification: ClassificationResult = await handle_webhook(req)
        logger.info(f"[Webhook] Classification complete: {classification.dict()}")
        
        return classification
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("[Webhook] Unexpected failure in /incoming")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )
