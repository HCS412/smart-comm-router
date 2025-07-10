import pytest
from unittest.mock import patch
from app.ingestion.sources import ingest_from_gmail, ingest_from_phone, IngestionError
from app.ingestion.gmail_client import GmailClient
from app.ingestion.twilio_client import TwilioClient

@pytest.fixture
def mock_gmail_client():
    """Mock GmailClient.fetch_latest_email method."""
    with patch("app.ingestion.sources.GmailClient") as mock:
        mock_instance = mock.return_value
        mock_instance.fetch_latest_email.return_value = {
            "sender": "mock.sender@gmail.com",
            "subject": "Invoice Issue",
            "content": "Hi, I noticed a discrepancy in my last invoice for $200.",
            "thread_id": "mock-thread-123",
            "labels": ["INBOX", "UNREAD"],
            "timestamp": "2025-07-10T12:00:00Z"
        }
        yield mock_instance

@pytest.fixture
def mock_twilio_client():
    """Mock TwilioClient.fetch_latest_voicemail method."""
    with patch("app.ingestion.sources.TwilioClient") as mock:
        mock_instance = mock.return_value
        mock_instance.fetch_latest_voicemail.return_value = {
            "sender": "+15551234567",
            "content": "This is a message regarding my recent delivery issue.",
            "call_sid": "mock-call-sid-456",
            "transcription_confidence": 0.92,
            "timestamp": "2025-07-10T12:00:00Z"
        }
        yield mock_instance

def test_ingest_from_gmail_mock(mock_gmail_client):
    """Test ingest_from_gmail with mock data."""
    result = ingest_from_gmail(mock=True)
    
    assert result["sender"] == "mock.sender@gmail.com"
    assert result["content"] == "Hi, I noticed a discrepancy in my last invoice for $200."
    assert result["source"] == "gmail"
    assert result["metadata"]["thread_id"] == "mock-thread-123"
    assert result["metadata"]["labels"] == ["INBOX", "UNREAD"]

def test_ingest_from_gmail_non_mock():
    """Test ingest_from_gmail with mock=False raises IngestionError."""
    with pytest.raises(IngestionError, match="Gmail integration is not implemented"):
        ingest_from_gmail(mock=False)

def test_ingest_from_gmail_empty_inbox(mock_gmail_client):
    """Test ingest_from_gmail with empty mock inbox."""
    mock_gmail_client.fetch_latest_email.side_effect = ValueError("No emails available in mock inbox")
    
    with pytest.raises(IngestionError, match="Gmail ingestion failed"):
        ingest_from_gmail(mock=True)

def test_ingest_from_phone_mock(mock_twilio_client):
    """Test ingest_from_phone with mock data."""
    result = ingest_from_phone(mock=True)
    
    assert result["sender"] == "+15551234567"
    assert result["content"] == "This is a message regarding my recent delivery issue."
    assert result["source"] == "phone"
    assert result["metadata"]["call_sid"] == "mock-call-sid-456"
    assert result["metadata"]["transcription_confidence"] == 0.92

def test_ingest_from_phone_non_mock():
    """Test ingest_from_phone with mock=False raises IngestionError."""
    with pytest.raises(IngestionError, match="Phone ingestion is not implemented"):
        ingest_from_phone(mock=False)

def test_ingest_from_phone_empty_inbox(mock_twilio_client):
    """Test ingest_from_phone with empty mock inbox."""
    mock_twilio_client.fetch_latest_voicemail.side_effect = ValueError("No voicemails available in mock inbox")
    
    with pytest.raises(IngestionError, match="Phone ingestion failed"):
        ingest_from_phone(mock=True)
