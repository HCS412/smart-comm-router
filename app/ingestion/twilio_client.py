from typing import Dict, Any
from app.utils.logger import logger

class TwilioClient:
    """
    Mock Twilio client for simulating voicemail transcription ingestion in the Triage Agent system.
    In a production environment, this would integrate with Twilio API to fetch voicemail transcriptions.
    """
    
    def __init__(self):
        """Initialize the mock Twilio client."""
        logger.info("[TwilioClient] Initialized mock Twilio client")
        self.mock_voicemails = [
            {
                "sender": "+15551234567",
                "content": "This is a message regarding my recent delivery issue.",
                "call_sid": "mock-call-sid-456",
                "transcription_confidence": 0.92,
                "timestamp": "2025-07-10T12:00:00Z"
            },
            {
                "sender": "+15559876543",
                "content": "I need to reschedule my pickup for next week.",
                "call_sid": "mock-call-sid-789",
                "transcription_confidence": 0.89,
                "timestamp": "2025-07-10T12:10:00Z"
            }
        ]
    
    def fetch_latest_voicemail(self) -> Dict[str, Any]:
        """
        Fetches the latest mock voicemail transcription.
        
        Returns:
            Dict[str, Any]: Mock voicemail data with sender, content, and metadata.
        
        Raises:
            ValueError: If no voicemails are available in the mock inbox.
        """
        if not self.mock_voicemails:
            logger.error("[TwilioClient] No mock voicemails available")
            raise ValueError("No voicemails available in mock inbox")
        
        voicemail = self.mock_voicemails[0]  # Simulate fetching the latest voicemail
        logger.info("[TwilioClient] Fetched mock voicemail from %s", voicemail["sender"])
        return voicemail
