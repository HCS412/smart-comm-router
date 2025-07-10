Smart Comm Router
Overview
The Smart Comm Router is an AI-powered system for auto-triaging and drafting responses to incoming messages, designed to streamline customer support workflows. It classifies messages by category, intent, priority, and queue, and generates tailored draft responses using a FastAPI backend and OpenAI's GPT-4 (mocked for demo purposes). The system supports mock ingestion from Gmail and phone sources, with a React frontend for user interaction. Built with scalability, reliability, and extensibility in mind, it includes robust error handling, logging, and unit tests, making it a production-ready prototype for demonstration.
Key features:

Message Classification: Categorizes messages (e.g., Billing, Dispatch) with confidence scores.
Draft Responses: Generates empathetic, context-aware replies based on classification.
Mock Ingestion: Simulates Gmail and phone inputs for testing without real API credentials.
Frontend UI: Provides a responsive interface for message submission and result visualization.
Comprehensive Testing: Includes unit tests for backend routes and ingestion logic.
Modular Design: Organized into agents, routes, services, and ingestion modules for easy extension.

Architecture

Backend: FastAPI with async support, Pydantic for validation, and mock ingestion for Gmail/phone.
Frontend: React with form validation, loading states, and visual confidence indicators.
AI Agents: ClassificationAgent and DraftResponseAgent for LLM-based processing (mocked).
Testing: Pytest-based unit tests for routes and ingestion.
Logging: Structured logging with structlog for traceability.

Setup Instructions
Prerequisites

Python (3.9+)
Node.js (v16+)
npm (v8+)
pip for Python package management

Backend Setup

Navigate to the root directory:
cd smart-comm-router


Install dependencies:
pip install -r requirements.txt


Create a .env file in the root directory using .env.example:
cp .env.example .env

Update .env with your OPENAI_API_KEY (use a mock key for demo, e.g., mock-openai-key).

Start the backend server:
uvicorn app.main:app --reload

The API will be available at http://localhost:8000.


Frontend Setup

Navigate to the frontend directory:cd frontend


Install dependencies:npm install


Create a .env file in the frontend directory:echo "REACT_APP_API_BASE_URL=http://localhost:8000" > .env


Start the development server:npm start

The app will be available at http://localhost:3000.

Environment Variables

Backend (./.env):
OPENAI_API_KEY: Mock or real OpenAI API key (required for demo).


Frontend (frontend/.env):
REACT_APP_API_BASE_URL: Backend API URL (default: http://localhost:8000).



Usage Guide
Frontend UI

Open http://localhost:3000 in your browser.
Enter a sender email (e.g., user@example.com), optional subject, and message content (minimum 10 characters).
Select a product (Discovery, Hauler, Pioneer).
Click "Classify & Draft" to process via the /triage endpoint.
View results:
Classification: Category, intent, priority, queue, and confidence (with progress bar).
Draft Response: AI-generated reply tailored to the message.
Errors are shown in a dismissible alert.



API Endpoints
Test endpoints using tools like Postman or curl. Base URL: http://localhost:8000.

POST /api/v1/messages/ingest:Ingests a mock message from Gmail or phone.
{
  "source": "gmail",
  "mock": true
}

Response: TriageOutput with classification and draft.

POST /api/v1/messages/classify:Classifies a message.
{
  "sender": "user@example.com",
  "content": "I have an invoice issue.",
  "metadata": {"product": "Discovery"}
}

Response: ClassificationOutput.

POST /api/v1/messages/draft:Generates a draft for a classified message.
{
  "sender": "user@example.com",
  "content": "I have an invoice issue.",
  "classification": {
    "category": "Billing Support",
    "intent": "Invoice Dispute",
    "confidence": 0.95
  }
}

Response: MessageOutput.

POST /api/v1/messages/triage:Combines classification and drafting.
{
  "sender": "user@example.com",
  "content": "I have an invoice issue.",
  "metadata": {"product": "Discovery"}
}

Response: TriageOutput.

POST /api/v1/webhooks/incoming:Processes mock webhook payloads (e.g., Gmail, Twilio).
{
  "from": "user@example.com",
  "message": "I need help with billing.",
  "channel": "gmail",
  "product": "Discovery"
}

Response: ClassificationResult.


Running Tests
Unit tests verify backend routes and ingestion logic.

Ensure dependencies are installed:pip install -r requirements.txt


Run tests:pytest tests/ -v

Tests cover:
API endpoints (/ingest, /classify, /draft, /triage).
Mock ingestion (gmail_client.py, twilio_client.py).



Project Structure
smart-comm-router/
├── app/                    # Backend source code
│   ├── agents/            # AI agents for classification and drafting
│   ├── ingestion/         # Mock Gmail and phone ingestion logic
│   ├── routes/            # FastAPI routes for API endpoints
│   ├── services/          # Webhook handling and normalization
│   └── utils/             # Logging and utilities
├── frontend/              # React frontend
│   ├── src/              # React components and app logic
│   └── README.md         # Frontend-specific documentation
├── tests/                # Unit tests for backend
├── .env.example          # Template for environment variables
├── requirements.txt       # Backend dependencies
└── README.md             # Project documentation

Contributing

Code Style: Use black and ruff for formatting and linting (black ., ruff check .).
Testing: Add tests in tests/ for new features, using pytest.
Pull Requests: Include clear descriptions and test results.
Mock-Based Design: Extend mock ingestion in app/ingestion/ for new sources.

Future Work

Real Integrations: Add Gmail and Twilio APIs by updating gmail_client.py and twilio_client.py.
Frontend Enhancements: Add source selector for /ingest in App.jsx.
Testing: Include frontend tests with react-testing-library.
Deployment: Containerize with Docker and deploy to AWS/GCP.
Security: Implement API key validation and rate limiting in production.

Notes

This is a mock-based prototype for demonstration, avoiding real API integrations for security and simplicity.
The system is designed for extensibility, with modular agents and ingestion logic.
Licensed under the MIT License.
