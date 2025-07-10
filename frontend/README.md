Triage Agent Frontend
Overview
The Triage Agent Frontend is a React-based user interface for the Triage Agent system, designed to streamline message classification and response drafting. It allows users to input messages, classify them using an AI-powered backend, and view structured classification results and draft responses. The frontend integrates seamlessly with the backend API, supporting mock ingestion from Gmail and phone sources, making it ideal for testing and demonstration purposes. Built with modern web technologies, it ensures a smooth, responsive, and accessible user experience.
Key features:

Input form for message submission with validation (email, content length).
Visual display of classification results (category, intent, priority, queue) with a confidence progress bar.
Draft response display for automated replies.
Support for mock ingestion from Gmail and phone sources via the /ingest endpoint.
Loading states and error handling for a polished UX.

Setup Instructions
Prerequisites

Node.js (v16 or higher)
npm (v8 or higher)
Backend API running at http://localhost:8000 (or configured via REACT_APP_API_BASE_URL)

Installation

Navigate to the frontend directory:
cd frontend


Install dependencies:
npm install


Create a .env file in the frontend directory and configure the API base URL:
echo "REACT_APP_API_BASE_URL=http://localhost:8000" > .env

Note: The default URL is http://localhost:8000. Adjust if your backend runs elsewhere.

Start the development server:
npm start

The app will be available at http://localhost:3000.


Environment Variables

REACT_APP_API_BASE_URL: The backend API URL (default: http://localhost:8000).Example: REACT_APP_API_BASE_URL=https://api.triage-agent.com

Usage Guide

Open the App: Navigate to http://localhost:3000 in your browser.
Submit a Message:
Enter a sender email (e.g., user@example.com).
Optionally provide a subject (e.g., "Invoice Issue").
Enter message content (minimum 10 characters).
Select a product (Discovery, Hauler, Pioneer).
Click "Classify & Draft" to process the message via the /triage endpoint.


View Results:
Classification Result: Displays category, intent, priority, queue, confidence (with progress bar), and fallback status.
Draft Response: Shows the AI-generated reply tailored to the message.
Errors (e.g., invalid email) are shown in a dismissible alert.


Test Ingestion (via API):
Use tools like Postman to test the /api/v1/messages/ingest endpoint:{
  "source": "gmail",
  "mock": true
}

or{
  "source": "phone",
  "mock": true
}


This returns a TriageOutput with classification and draft response.



Dependencies

react (18.2.0): Core library for building the UI.
react-dom (18.2.0): Handles DOM rendering.
react-hook-form (7.51.0): Form validation and management.
axios (1.4.0): HTTP client for API requests.
axios-retry (4.0.0): Retries failed API calls for reliability.
react-progressbar (15.4.1): Visual progress bar for confidence scores.
react-scripts (5.0.1): Build and development tools.

Development Notes

Extending the Frontend:

Add new components in src/components/ for modularity.
Enhance App.jsx to support source selection (e.g., dropdown for Gmail/phone ingestion).
Consider adding a history view to display past classifications.


Styling:

Uses Tailwind-inspired CSS for a modern, responsive design.
Customize styles in public/index.html or component-level classes.


Mock Data:

The frontend integrates with mock Gmail and phone ingestion for demonstration purposes.
Real API integrations (e.g., Google Gmail API, Twilio) can be added by updating app/ingestion/ modules.


Contributing:

Follow coding standards (e.g., Prettier, ESLint if added).
Test changes with the backend running.
Submit pull requests with clear descriptions of changes.



Notes

This is a mock-based prototype for demonstration, avoiding real API integrations for security and simplicity.
For production, secure the backend with API keys and add real ingestion sources (see app/ingestion/).
The frontend is accessible, with ARIA attributes for screen reader support.
