from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.schemas.message import Message
from app.agents.classify_agent import classify_message
from app.utils.logger import logger
from datetime import datetime

router = APIRouter()


@router.post("/classify", summary="Classify a communication message", response_description="Classification result")
async def classify_message_route(request: Request, msg: Message):
    """
    Classify a message for DSQ Technology use cases.
    
    The agent will analyze the message content and metadata to determine:
    - Category (e.g. 'Billing Support', 'Sensor Alert')
    - Priority (High, Medium, Low)
    - Intent (user's goal or issue)
    - Recommended queue/team to handle the message
    - Confidence score from classification model
    
    Examples of supported product types:
    - Discovery (billing & audit support)
    - Hauler (dispatch/scheduling)
    - Pioneer (sensor/monitoring alerts)
    """
    try:
        logger.info(f"[{datetime.utcnow()}] New message received from {msg.sender}")

        result = classify_message(msg.dict())

        logger.info(f"[{datetime.utcnow()}] Classification result: {result}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "input_summary": {
                    "sender": msg.sender,
                    "subject": msg.subject,
                    "product": msg.product,
                    "channel": msg.channel
                },
                "classification": result
            }
        )

    except Exception as e:
        logger.error(f"Error during classification: {e}")
        raise HTTPException(status_code=500, detail="Classification failed")
