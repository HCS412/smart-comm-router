# app/routes/messages.py

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.agents.draft_response_agent import DraftResponseAgent
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

class MessageOutput(BaseModel):
    reply_draft: str
    confidence: float
    fallback_used: bool
    error: Optional[str]
    _agent: Optional[str]
    _version: Optional[str]
    _latency_ms: Optional[float]

# ----------- Agent Instance --------------
agent: BaseAgent = DraftResponseAgent()

# ----------- API Endpoint --------------

@router.post("/draft", response_model=MessageOutput, summary="Generate draft reply", tags=["Messages"])
async def draft_reply(payload: MessageInput, request: Request):
    try:
        # Set request metadata for traceability
        agent.set_metadata({
            "request_id": getattr(request.state, "request_id", "unknown"),
            "ip": request.client.host
        })

        logger.info(f"[DraftRoute] Processing message from {payload.sender}")

        result = agent.execute(payload.dict())
        return result

    except Exception as e:
        logger.exception("[DraftRoute] Failure in draft endpoint")
        raise HTTPException(status_code=500, detail="Agent failed to generate a draft reply")
