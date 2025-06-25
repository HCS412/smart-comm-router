from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    sender: str
    content: str
    timestamp: datetime
