from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.agents.draft_response_agent import DraftResponseAgent
from app.agents.classify_agent import ClassificationAgent
from app.agents.base_agent import BaseAgent
from app.utils.logger import logger
from app.ingestion.sources import ingest_from_gmail, ingest_from_phone

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

class IngestInput(BaseModel):
    source: str = Field(..., example="gmail", description="Source of the message: 'gmail' or 'phone'")
    mock: bool = Field(True, description="Use mock data for ingestion (always True in prototype)")

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

class TriageOutput(BaseModel):
    classification: ClassificationOutput
    draft: MessageOutput

# ----------- Agent Instances --------------
draft_agent: BaseAgent = DraftResponseAgent()
classify_agent: BaseAgent = ClassificationAgent()

# ----------- API Endpoints --------------
@router.post("/ingest", response_model=TriageOutput, summary="Ingest a message from a specified source and triage it")
async def ingest_message(payload: IngestInput, request: Request):
    """
    Ingests a message from a specified source (gmail or phone) and processes it through the triage pipeline.
    
    Args:
        payload: IngestInput with source ('gmail' or 'phone') and mock flag.
        request: FastAPI Request object for metadata.
    
    Returns:
        TriageOutput with classification and draft response.
    
    Raises:
        HTTPException: For invalid sources or ingestion failures.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host
    
    if payload.source not in ["gmail", "phone"]:
        logger.error("[IngestRoute] Invalid source: %s", payload.source)
        raise HTTPException(status_code=400, detail="Invalid source. Must be 'gmail' or 'phone'.")
    
    try:
        # Ingest message based on source
        logger.info(f"[IngestRoute] Ingesting from {payload.source} (mock: {payload.mock})")
        message = (
            ingest_from_gmail(mock=payload.mock)
            if payload.source == "gmail"
            else ingest_from_phone(mock=payload.mock)
        )
        
        # Step 1: Classify
        classify_agent.set_metadata({"request_id": request_id, "ip": client_ip})
        logger.info(f"[IngestRoute] Classifying message from {message['sender']}")
        classification_result = await classify_agent.execute({
            "sender": message["sender"],
            "content": message["content"],
            "metadata": message["metadata"]
        })
        
        # Step 2: Generate Draft
        draft_agent.set_metadata({"request_id": request_id, "ip": client_ip})
        logger.info(f"[IngestRoute] Drafting reply for {message['sender']}")
        draft_result = await draft_agent.execute({
            "sender": message["sender"],
            "content": message["content"],
            "classification": classification_result,
            "metadata": message["metadata"]
        })
        
        return {
            "classification": classification_result,
            "draft": draft_result
        }
    except Exception as e:
        logger.exception("[IngestRoute] Failure during ingestion and triage")
        raise HTTPException(status_code=500, detail=f"Ingestion and triage failed: {str(e)}")

@router.post("/draft", response_model=MessageOutput, summary="Generate draft reply to a classified message")
async def draft_reply(payload: MessageInput, request: Request):
    """
    Generates a draft reply for a pre-classified message.
    """
    try:
        draft_agent.set_metadata({
            "request_id": getattr(request.state, "request_id", "unknown"),
            "ip": request.client.host
        })
        logger.info(f"[DraftRoute] Processing message from: {payload.sender}")
        result = await draft_agent.execute(payload.dict())
        return result
    except Exception as e:
        logger.exception("[DraftRoute] Failure during draft generation")
        raise HTTPException(status_code=500, detail=f"Draft agent failed: {str(e)}")

@router.post("/classify", response_model=ClassificationOutput, summary="Classify an inbound message")
async def classify_message(payload: RawMessageInput, request: Request):
    """
    Classifies an inbound message by category, intent, priority, and queue.
    """
    try:
        classify_agent.set_metadata({
            "request_id": getattr(request.state, "request_id", "unknown"),
            "ip": request.client.host
        })
        logger.info(f"[ClassifyRoute] Classifying message from: {payload.sender}")
        result = await classify_agent.execute(payload.dict())
        return result
    except Exception as e:
        logger.exception("[ClassifyRoute] Failure during classification")
        raise HTTPException(status_code=500, detail=f"Classification agent failed: {str(e)}")

@router.post("/triage", response_model=TriageOutput, summary="Classify and generate a draft reply")
async def triage_message(payload: RawMessageInput, request: Request):
    """
    Classifies an inbound message and generates a draft reply in one step.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host
    
    try:
        # Step 1: Classify
        classify_agent.set_metadata({"request_id": request_id, "ip": client_ip})
        logger.info(f"[TriageRoute] Classifying message from {payload.sender}")
        classification_result = await classify_agent.execute({
            "sender": payload.sender,
            "content": payload.content,
            "metadata": payload.metadata
        })
        
        # Step 2: Generate Draft
        draft_agent.set_metadata({"request_id": request_id, "ip": client_ip})
        logger.info(f"[TriageRoute] Drafting reply for {payload.sender}")
        draft_result = await draft_agent.execute({
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
        raise HTTPException(status_code=500, detail=f"Triage agent failed: {str(e)}")
