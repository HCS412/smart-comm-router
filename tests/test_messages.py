import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.agents.base_agent import AgentOutput, AgentInput

@pytest.fixture
def client():
    """Create a FastAPI test client."""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Create an async HTTPX client for testing async endpoints."""
    return AsyncClient(app=app, base_url="http://test")

@pytest.fixture
def mock_classify_agent():
    """Mock ClassificationAgent.execute method."""
    with patch("app.routes.messages.ClassificationAgent") as mock:
        mock_instance = mock.return_value
        mock_instance.execute = AsyncMock(return_value=AgentOutput(
            category="Billing Support",
            intent="Invoice Dispute",
            priority="High",
            recommended_queue="Finance Support",
            confidence=0.95,
            fallback_used=False,
            error=None,
            _agent="ClassificationAgent",
            _version="2.0.0",
            _latency_ms=100.0
        ))
        mock_instance.set_metadata = AsyncMock()
        yield mock_instance

@pytest.fixture
def mock_draft_agent():
    """Mock DraftResponseAgent.execute method."""
    with patch("app.routes.messages.DraftResponseAgent") as mock:
        mock_instance = mock.return_value
        mock_instance.execute = AsyncMock(return_value=AgentOutput(
            reply_draft="Thank you for your message. We'll review your invoice and respond within 24 hours.",
            category="Billing Support",
            intent="Invoice Dispute",
            priority="High",
            recommended_queue="Finance Support",
            confidence=0.95,
            fallback_used=False,
            error=None,
            _agent="DraftResponseAgent",
            _version="2.0.0",
            _latency_ms=150.0
        ))
        mock_instance.set_metadata = AsyncMock()
        yield mock_instance

@pytest.mark.asyncio
async def test_ingest_endpoint_gmail(async_client, mock_classify_agent, mock_draft_agent):
    """Test the /ingest endpoint with mock Gmail source."""
    payload = {"source": "gmail", "mock": True}
    response = await async_client.post("/api/v1/messages/ingest", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert data["classification"]["category"] == "Billing Support"
    assert data["classification"]["intent"] == "Invoice Dispute"
    assert "draft" in data
    assert "Thank you for your message" in data["draft"]["reply_draft"]

@pytest.mark.asyncio
async def test_ingest_endpoint_phone(async_client, mock_classify_agent, mock_draft_agent):
    """Test the /ingest endpoint with mock phone source."""
    payload = {"source": "phone", "mock": True}
    response = await async_client.post("/api/v1/messages/ingest", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert data["classification"]["category"] == "Billing Support"
    assert "draft" in data

@pytest.mark.asyncio
async def test_ingest_endpoint_invalid_source(async_client):
    """Test the /ingest endpoint with an invalid source."""
    payload = {"source": "invalid", "mock": True}
    response = await async_client.post("/api/v1/messages/ingest", json=payload)
    
    assert response.status_code == 400
    assert "Invalid source" in response.json()["detail"]

@pytest.mark.asyncio
async def test_classify_endpoint(async_client, mock_classify_agent):
    """Test the /classify endpoint with valid input."""
    payload = {
        "sender": "test@example.com",
        "content": "I have an issue with my invoice.",
        "metadata": {"product": "Discovery"}
    }
    response = await async_client.post("/api/v1/messages/classify", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Billing Support"
    assert data["intent"] == "Invoice Dispute"
    assert data["confidence"] == 0.95

@pytest.mark.asyncio
async def test_classify_endpoint_missing_content(async_client):
    """Test the /classify endpoint with missing content."""
    payload = {
        "sender": "test@example.com",
        "metadata": {"product": "Discovery"}
    }
    response = await async_client.post("/api/v1/messages/classify", json=payload)
    
    assert response.status_code == 422  # Unprocessable Entity
    assert "content" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_draft_endpoint(async_client, mock_draft_agent):
    """Test the /draft endpoint with valid input."""
    payload = {
        "sender": "test@example.com",
        "content": "I have an issue with my invoice.",
        "classification": {
            "category": "Billing Support",
            "intent": "Invoice Dispute",
            "confidence": 0.95
        }
    }
    response = await async_client.post("/api/v1/messages/draft", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "Thank you for your message" in data["reply_draft"]
    assert data["confidence"] == 0.95

@pytest.mark.asyncio
async def test_triage_endpoint(async_client, mock_classify_agent, mock_draft_agent):
    """Test the /triage endpoint with valid input."""
    payload = {
        "sender": "test@example.com",
        "content": "I have an issue with my invoice.",
        "metadata": {"product": "Discovery"}
    }
    response = await async_client.post("/api/v1/messages/triage", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert data["classification"]["category"] == "Billing Support"
    assert "draft" in data
    assert "Thank you for your message" in data["draft"]["reply_draft"]
