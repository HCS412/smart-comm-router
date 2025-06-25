# app/routes/messages.py

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.agents.draft_response_agent import DraftResponseAgent
from app.agents.classify_agent import ClassifyAgent
from app.agents.base_agent import BaseAgent
from app.utils.logger import logger

router = APIRouter()

# ----------- Pydantic Models --------------

class ClassificationInput(BaseModel):
    category: str
    intent: str
    confidence: Optional[float] = 0.85

class MessageInput(BaseModel):
    sender: str = Field(..., example="jane.doe@example.com")
    content: str = Field(..., example="Hello, I need help with billing.")
    classification: ClassificationInput

class RawMessageInput(BaseModel):
    sender: str = Field(..., example="john@example.com")
    content: str = Field(..., example="I need support with my account.")

class MessageOutput(BaseModel):
    reply_draft: str
    confidence: float
    fallback_used: bool
    error: Optional[str]
    _agent: Optional[str]
    _version: Optional[str]
    _latency_ms: Optional[float]

class ClassificationOutput(BaseModel):
    category: str
    intent: str
    priority: str
    recommended_queue: str
    confidence: float
    fallback_used: bool
    error: Optional[str]
    _agent: Optional[str]
    _version: Optional[str]
    _latency_ms: Optional[float]

# ----------- Agent Instances --------------
draft_agent: BaseAgent = DraftResponseAgent()
classify_agent: BaseAgent = ClassifyAgent()

# ----------- API Endpoints --------------

@router.post("/draft", response_model=MessageOutput, summary="Generate draft reply", tags=["Messages"])
async def draft_reply(payload: MessageInput, request: Request):
    try:
        draft_agent.set_metadata({
            "request_id": getattr(request.state, "request_id", "unknown"),
            "ip": request.client.host
        })

        logger.info(f"[DraftRoute] Processing message from {payload.sender}")

        result = draft_agent.execute(payload.dict())
        return result

    except Exception as e:
        logger.exception("[DraftRoute] Failure in draft endpoint")
        raise HTTPException(status_code=500, detail="Agent failed to generate a draft reply")

@router.post("/classify", response_model=ClassificationOutput, summary="Classify an inbound message", tags=["Messages"])
async def classify_message(payload: RawMessageInput, request: Request):
    try:
        classify_agent.set_metadata({
            "request_id": getattr(request.state, "request_id", "unknown"),
            "ip": request.client.host
        })

        logger.info(f"[ClassifyRoute] Classifying message from {payload.sender}")

        result = classify_agent.execute(payload.dict())
        return result

    except Exception as e:
        logger.exception("[ClassifyRoute] Failure in classify endpoint")
        raise HTTPException(status_code=500, detail="Agent failed to classify message")
