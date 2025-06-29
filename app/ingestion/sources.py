# app/ingestion/sources.py

from typing import Dict, Any
from app.utils.logger import logger

def ingest_from_gmail(mock: bool = True) -> Dict[str, Any]:
    """
    Placeholder function for Gmail message ingestion.
    """
    logger.info("[GmailIngestion] Ingesting message (mock mode: %s)", mock)

    if mock:
        return {
            "sender": "mock.sender@gmail.com",
            "content": "Hi, I need help with my last invoice.",
            "source": "gmail",
            "metadata": {
                "thread_id": "mock-thread-123",
                "labels": ["INBOX", "UNREAD"]
            }
        }

    raise NotImplementedError("Gmail integration is not yet implemented.")


def ingest_from_phone(mock: bool = True) -> Dict[str, Any]:
    """
    Placeholder function for phone (voicemail/transcription) ingestion.
    """
    logger.info("[PhoneIngestion] Ingesting voicemail (mock mode: %s)", mock)

    if mock:
        return {
            "sender": "+15551234567",
            "content": "This is a message regarding my recent delivery issue.",
            "source": "phone",
            "metadata": {
                "call_sid": "mock-call-sid-456",
                "transcription_confidence": 0.92
            }
        }

    raise NotImplementedError("Phone ingestion integration is not yet implemented.")
