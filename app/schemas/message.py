from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class Message(BaseModel):
    sender: str = Field(..., example="customer@example.com")
    subject: Optional[str] = Field(None, example="Invoice discrepancy Q2")
    content: str = Field(..., example="I see a surcharge I don't recognize on invoice #123.")
    channel: Optional[str] = Field("email", example="email")  # "sms", "webhook"
    product: Optional[str] = Field(None, example="Discovery")  # Could be 'Discovery', 'Hauler', 'Pioneer'
    timestamp: Optional[datetime] = Field(None, example="2025-06-25T10:30:00Z")
    attachments: Optional[List[str]] = Field(None)
