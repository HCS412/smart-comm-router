from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.schemas.message import Message
from app.agents.classify_agent import classify_message
from app.agents.draft_response_agent import DraftResponseAgent
from app.utils.logger import logger

router = APIRouter()

# ----------- Models -----------

class DraftRequest(BaseModel):
    sender: str
    content: str
    classification: Dict[str, Any] = Field(..., description="Pre-classified metadata for this message")


class DraftResponse(BaseModel):
    reply_draft: str
    confidence: float
    latency_ms: float
    fallback_used: bool
    error: Optional[str] = None

# ----------- Routes -----------

@router.post("/classify", summary="Classify a message", tags=["Classification"])
def classify(msg: Message):
    """
    Takes a raw message and returns classification metadata.
    """
    try:
        logger.info(f"[Classify] Message received from {msg.sender}")
        result = classify_message(msg.dict())
        logger.info(f"[Classify] Classification result: {result}")
        return {"classification": result}
    except Exception as e:
        logger.exception("[Classify] Failed to classify")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft", response_model=DraftResponse, summary="Generate a reply draft", tags=["Drafting"])
def generate_draft(body: DraftRequest):
    """
    Takes a message + classification and returns a smart AI-generated reply draft.
    """
    try:
        logger.info(f"[Draft] Generating reply for sender {body.sender}")
        agent = DraftResponseAgent()
        result = agent.execute(body.dict())
        return result
    except Exception as e:
        logger.exception("[Draft] Failed to generate reply")
        raise HTTPException(status_code=500, detail=str(e))
