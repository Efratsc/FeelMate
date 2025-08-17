from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="FeelMate API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FeelMate Emotional Support API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/chat/send-message")
async def send_message(message: dict):
    """Simple chat endpoint for testing"""
    return {
        "response": "I understand how you're feeling. I'm here to listen and support you.",
        "emotion": "neutral",
        "severity": 4,
        "confidence": 0.8,
        "needs_help": False,
        "resources": [],
        "session_id": "test-session"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
