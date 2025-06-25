from fastapi import APIRouter
from app.schemas.message import Message
from app.agents.classify_agent import classify_message

router = APIRouter()

@router.post("/classify")
def classify(msg: Message):
    """Classify an incoming message using the AI agent"""
    result = classify_message(msg.content)
    return {"classification": result}
