from fastapi import FastAPI

app = FastAPI(title="Triage Agent API")

@app.get("/")
def read_root():
    return {"message": "Triage Agent API is running!"}
