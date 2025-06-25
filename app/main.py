from fastapi import FastAPI
from app.routes.inbox import router as inbox_router

app = FastAPI(
    title="Triage Agent API",
    description="Agent-based system for auto-triaging incoming communications",
    version="0.1.0"
)

# Route registrations
app.include_router(inbox_router, prefix="/api/inbox", tags=["Inbox"])

@app.get("/")
def root():
    return {"message": "Welcome to the Triage Agent API!"}
