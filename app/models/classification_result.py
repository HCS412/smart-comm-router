from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime

class ClassificationResult(BaseModel):
    """
    A structured classification result for incoming communication messages.
    Used across routes, services, and external integrations.
    """

    category: Literal[
        "Billing Support",
        "Dispatch Communication",
        "Sensor Alert",
        "Marketing",
        "General Inquiry"
    ] = Field(..., description="High-level message type")

    priority: Literal["High", "Medium", "Low"] = Field(
        ..., description="Operational urgency"
    )

    intent: str = Field(
        ..., example="Invoice Dispute", description="User's objective or issue"
    )

    recommended_queue: Literal[
        "Finance Support", "Dispatch Team", "Ops Team", "Automation", "Customer Support"
    ] = Field(..., description="Which internal team should own this")

    confidence: float = Field(
        ..., ge=0.0, le=1.0, example=0.94, description="LLM model certainty (0.0–1.0)"
    )

    classified_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when classification occurred"
    )

    fallback_used: Optional[bool] = Field(
        default=False,
        description="If classification relied on a fallback rule or default"
    )

    error: Optional[str] = Field(
        default=None,
        description="Optional error message if fallback or LLM failure occurred"
    )

    @validator("intent")
    def strip_intent(cls, v):
        return v.strip().capitalize()

    class Config:
        schema_extra = {
            "example": {
                "category": "Billing Support",
                "priority": "High",
                "intent": "Duplicate Charge",
                "recommended_queue": "Finance Support",
                "confidence": 0.91,
                "classified_at": "2025-06-25T15:47:00Z",
                "fallback_used": False,
                "error": None
            }
        }
