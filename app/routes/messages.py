from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.agents.draft_response_agent import DraftResponseAgent
from app.agents.classify_agent import ClassifyAgent
from app.agents.base_agent import BaseAgent
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])

# ----------- Pydantic Models --------------

class ClassificationInput(BaseModel):
    category: str = Field(..., example="Billing Support")
    intent: str = Field(..., example="Refund Request")
    confidence: Optional[float] = Field(0.85, ge=0.0, le=1.0)

class MessageInput(BaseModel):
    sender: str = Field(..., example="jane.doe@example.com")
    content: str = Field(..., example="Hello, I need help with billing.")
    classification: ClassificationInput

class RawMessageInput(BaseModel):
    sender: str = Field(..., example="john@example.com")
    content: str = Field(..., example="I need support with my account.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MessageOutput(BaseModel):
    reply_draft: str
    confidence: float
    fallback_used: bool
    error: Optional[str] = None
    _agent: Optional[str] = None
    _version: Optional[str] = None
    _latency_ms: Optional[float] = None

class ClassificationOutput(BaseModel):
    category: str
    intent: str
    priority: str
    recommended_queue: str
    confidence: float
    fallback_used: bool
    error: Optional[str] = None
    _agent: Optional[str] = None
    _version: Optional[str] = None
    _latency_ms: Optional[float] = None

# ----------- Agent Instances --------------

draft_agent: BaseAgent = DraftResponseAgent()
classify_agent: BaseAgent = ClassifyAgent()

# ----------- API Endpoints --------------

@router.post("/draft", response_model=MessageOutput, summary="Generate draft reply to a classified message")
async def draft_reply(payload: MessageInput, request: Request):
    try:
        draft_agent.set_metadata({
            "request_id": getattr(request.state, "request_id", "unknown"),
            "ip": request.client.host
        })
        logger.info(f"[DraftRoute] Processing message from: {payload.sender}")
        result = draft_agent.execute(payload.dict())
        return result
    except Exception as e:
        logger.exception("[DraftRoute] Failure during draft generation")
        raise HTTPException(status_code=500, detail="Draft agent failed to generate a response")

@router.post("/classify", response_model=ClassificationOutput, summary="Classify an inbound message by category, intent, and routing")
async def classify_message(payload: RawMessageInput, request: Request):
    try:
        classify_agent.set_metadata({
            "request_id": getattr(request.state, "request_id", "unknown"),
            "ip": request.client.host
        })
        logger.info(f"[ClassifyRoute] Classifying message from: {payload.sender}")
        result = classify_agent.execute(payload.dict())
        return result
    except Exception as e:
        logger.exception("[ClassifyRoute] Failure during classification")
        raise HTTPException(status_code=500, detail="Classification agent failed to process message")

class TriageInput(BaseModel):
    sender: str = Field(..., example="casey@example.com")
    content: str = Field(..., example="Can you help me cancel my plan?")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TriageOutput(BaseModel):
    classification: ClassificationOutput
    draft: MessageOutput

@router.post("/triage", response_model=TriageOutput, summary="Classify and generate a draft reply", tags=["Messages"])
async def triage_message(payload: TriageInput, request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host

    try:
        # Step 1: Classify
        classify_agent.set_metadata({"request_id": request_id, "ip": client_ip})
        logger.info(f"[Triage] Classifying message from {payload.sender}")
        classification_result = classify_agent.execute({
            "sender": payload.sender,
            "content": payload.content,
            "metadata": payload.metadata
        })

        # Step 2: Generate Draft
        draft_agent.set_metadata({"request_id": request_id, "ip": client_ip})
        logger.info(f"[Triage] Drafting reply for {payload.sender}")
        draft_result = draft_agent.execute({
            "sender": payload.sender,
            "content": payload.content,
            "classification": classification_result,
            "metadata": payload.metadata
        })

        return {
            "classification": classification_result,
            "draft": draft_result
        }

    except Exception as e:
        logger.exception("[TriageRoute] Failure during triage processing")
        raise HTTPException(status_code=500, detail="Triage agent failed to process message")

