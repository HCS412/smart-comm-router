from fastapi import APIRouter, Request, Header, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.webhook_handler import handle_webhook
from app.models.classification_result import ClassificationResult
from app.utils.logger import logger
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.post(
    "/incoming",
    response_model=ClassificationResult,
    summary="Public webhook endpoint",
    response_description="Structured classification of the message"
)
async def webhook_entrypoint(
    req: Request,
    x_api_key: Optional[str] = Header(None, description="Optional API key for webhook security")
):
    """
    Accepts an inbound message payload from external services (n8n, Zapier, email parser, etc.),
    normalizes it, classifies it using LLMs, and returns a validated structured response.

    ### Headers
    - `X-API-Key`: Optional token-based protection (to be enforced in future)

    ### Payload Examples:
    ```json
    {
      "from": "client@example.com",
      "subject": "Roll-off ETA missing",
      "message": "Hi, we scheduled a pickup but haven’t received an ETA.",
      "channel": "email",
      "product": "Hauler"
    }
    ```
    """
    try:
        logger.info(f"[Webhook] Request received at {datetime.utcnow().isoformat()}")

        # TODO: If needed, validate x_api_key here in the future
        # Example: raise HTTPException(status_code=403, detail="Invalid API Key")

        classification: ClassificationResult = await handle_webhook(req)

        return classification

    except HTTPException as he:
        raise he  # Pass through intentional HTTP errors

    except Exception as e:
        logger.exception("[Webhook] Unexpected failure in /incoming")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unhandled classification error: {str(e)}"
        )
