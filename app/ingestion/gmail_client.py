from typing import Dict, Any
from app.utils.logger import logger

class GmailClient:
    """
    Mock Gmail client for simulating email ingestion in the Triage Agent system.
    In a production environment, this would integrate with Google Gmail API using OAuth2.
    """
    
    def __init__(self):
        """Initialize the mock Gmail client."""
        logger.info("[GmailClient] Initialized mock Gmail client")
        self.mock_emails = [
            {
                "sender": "mock.sender@gmail.com",
                "subject": "Invoice Issue",
                "content": "Hi, I noticed a discrepancy in my last invoice for $200.",
                "thread_id": "mock-thread-123",
                "labels": ["INBOX", "UNREAD"],
                "timestamp": "2025-07-10T12:00:00Z"
            },
            {
                "sender": "client@example.com",
                "subject": "Pickup Schedule",
                "content": "When is my next pickup scheduled?",
                "thread_id": "mock-thread-456",
                "labels": ["INBOX"],
                "timestamp": "2025-07-10T12:05:00Z"
            }
        ]
    
    def fetch_latest_email(self) -> Dict[str, Any]:
        """
        Fetches the latest mock email from the simulated inbox.
        
        Returns:
            Dict[str, Any]: Mock email data with sender, subject, content, and metadata.
        
        Raises:
            ValueError: If no emails are available in the mock inbox.
        """
        if not self.mock_emails:
            logger.error("[GmailClient] No mock emails available")
            raise ValueError("No emails available in mock inbox")
        
        email = self.mock_emails[0]  # Simulate fetching the latest email
        logger.info("[GmailClient] Fetched mock email from %s", email["sender"])
        return email
