from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.logger import logger
from app.ingestion.gmail_client import GmailClient
from app.ingestion.twilio_client import TwilioClient

class IngestionError(Exception):
    """Custom exception for ingestion-related errors."""
    pass

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def ingest_from_gmail(mock: bool = True) -> Dict[str, Any]:
    """
    Ingests a message from Gmail (mock implementation for demonstration).
    
    Args:
        mock (bool): If True, uses mock data; if False, raises NotImplementedError for real API.
    
    Returns:
        Dict[str, Any]: Normalized message data with sender, content, source, and metadata.
    
    Raises:
        IngestionError: If mock is False (real API not implemented).
        Exception: For unexpected errors during ingestion.
    """
    logger.info("[GmailIngestion] Ingesting message (mock mode: %s)", mock)
    
    if not mock:
        raise IngestionError("Gmail integration is not implemented in this prototype.")
    
    try:
        client = GmailClient()
        email = client.fetch_latest_email()
        return {
            "sender": email["sender"],
            "content": email["content"],
            "subject": email.get("subject", "(no subject)"),
            "source": "gmail",
            "metadata": {
                "thread_id": email.get("thread_id", "mock-thread-123"),
                "labels": email.get("labels", ["INBOX", "UNREAD"]),
                "timestamp": email.get("timestamp", "2025-07-10T12:00:00Z")
            }
        }
    except Exception as e:
        logger.error("[GmailIngestion] Failed to ingest: %s", str(e))
        raise IngestionError(f"Gmail ingestion failed: {str(e)}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def ingest_from_phone(mock: bool = True) -> Dict[str, Any]:
    """
    Ingests a voicemail transcription from phone (mock implementation for demonstration).
    
    Args:
        mock (bool): If True, uses mock data; if False, raises NotImplementedError for real API.
    
    Returns:
        Dict[str, Any]: Normalized message data with sender, content, source, and metadata.
    
    Raises:
        IngestionError: If mock is False (real API not implemented).
        Exception: For unexpected errors during ingestion.
    """
    logger.info("[PhoneIngestion] Ingesting voicemail (mock mode: %s)", mock)
    
    if not mock:
        raise IngestionError("Phone ingestion is not implemented in this prototype.")
    
    try:
        client = TwilioClient()
        voicemail = client.fetch_latest_voicemail()
        return {
            "sender": voicemail["sender"],
            "content": voicemail["content"],
            "source": "phone",
            "metadata": {
                "call_sid": voicemail.get("call_sid", "mock-call-sid-456"),
                "transcription_confidence": voicemail.get("transcription_confidence", 0.92),
                "timestamp": voicemail.get("timestamp", "2025-07-10T12:00:00Z")
            }
        }
    except Exception as e:
        logger.error("[PhoneIngestion] Failed to ingest: %s", str(e))
        raise IngestionError(f"Phone ingestion failed: {str(e)}")
