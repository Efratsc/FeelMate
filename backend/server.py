"""
Production FastAPI server for FeelMate Emotion-Aware Chatbot
CPU-only version with PostgreSQL LangChain memory integration
"""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from chatbot import get_chatbot, ChatResponse
from config import FRONTEND_URLS, HOST, PORT, RELOAD, LOG_LEVEL
from postgres_memory import cleanup_expired_sessions
from user_session import get_user_session_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="FeelMate Emotion-Aware Chatbot",
    description="Production-ready supportive chatbot with PostgreSQL LangChain memory",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
chatbot = get_chatbot()
user_session_manager = get_user_session_manager()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: str

class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_activity: Optional[str] = None
    current_emotion: Optional[str] = None
    severity_level: Optional[str] = None
    is_active: bool = True
    message_count: int = 0

class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, str]]

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting FeelMate Production Emotion-Aware Chatbot...")
    logger.info("✅ Server ready to accept requests")
    logger.info("💡 Using CPU-only emotion detection with GPT-2")
    logger.info("🗄️ PostgreSQL LangChain memory integration active")

@app.get("/")
async def root():
    return {
        "message": "FeelMate Emotion-Aware Chatbot API",
        "version": "1.0.0",
        "status": "production",
        "features": [
            "CPU-only emotion detection",
            "PostgreSQL LangChain memory",
            "Intelligent response templates",
            "Crisis detection",
            "Conversation memory",
            "Resource recommendations"
        ],
        "endpoints": {
            "/api/chat/send-message": "POST - Send a message and get response",
            "/api/chat/session/{session_id}": "GET - Get session information",
            "/api/chat/history/{session_id}": "GET - Get conversation history",
            "/api/chat/sessions/{user_id}": "GET - Get user's active sessions",
            "/health": "GET - Check server health",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FeelMate Production Chatbot",
        "model": "CPU-only emotion detection with PostgreSQL memory",
        "version": "1.0.0"
    }

@app.post("/api/chat/send-message")
async def send_message(request: ChatMessage):
    """
    Main chat endpoint with PostgreSQL LangChain memory integration
    NOW: Trusts that user is already authenticated by better-auth
    """
    try:
        # Since better-auth already authenticated the user, we trust the user_id
        # Skip additional validation for now to avoid double authentication
        logger.info(f"Chat request from user ID: {request.user_id}")
        
        # Process chat request directly
        response = chatbot.chat(
            user_message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )

        return {
            "response": response.response,
            "emotion": response.emotion,
            "severity": response.severity,
            "crisis_detected": response.crisis_detected,
            "session_id": response.session_id,
            "user_info": {
                "user_id": request.user_id,
                "email": f"user_{request.user_id}@feelmate.com"  # Placeholder
            }
        }

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/chat/session/{session_id}")
async def get_session_info(session_id: str, user_id: str):
    """
    Get detailed session information
    """
    try:
        session_info = chatbot.get_session_info(session_id, user_id)
        return SessionInfo(**session_info)
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session information")

@app.get("/api/chat/history/{session_id}")
async def get_conversation_history(session_id: str, user_id: str):
    """
    Get conversation history for a specific session
    """
    try:
        messages = chatbot.get_conversation_history(session_id, user_id)
        return ConversationHistory(session_id=session_id, messages=messages)
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation history")

@app.get("/api/chat/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """
    Get all active sessions for a user
    """
    try:
        # Get user's chat history without additional validation
        sessions = user_session_manager.get_user_chat_history(user_id=user_id, limit=20)
        
        return {
            "user_id": user_id,
            "user_email": f"user_{user_id}@feelmate.com",  # Placeholder
            "active_sessions": sessions,
            "total_sessions": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user sessions")

@app.post("/api/chat/cleanup-sessions")
async def cleanup_sessions():
    """
    Clean up expired sessions (admin endpoint)
    """
    try:
        cleanup_expired_sessions(timeout_minutes=30)
        return {"message": "Session cleanup completed", "status": "success"}
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup sessions")

@app.post("/api/chat/cleanup-user-sessions/{user_id}")
async def cleanup_user_sessions(user_id: str):
    """
    Clean up expired sessions for a specific user
    """
    try:
        # Clean up user's expired sessions without validation
        cleaned_count = user_session_manager.cleanup_user_sessions(user_id=user_id, timeout_hours=24)
        
        return {
            "message": f"Cleaned up {cleaned_count} expired sessions",
            "user_id": user_id,
            "cleaned_count": cleaned_count,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error cleaning up user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup user sessions")

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level=LOG_LEVEL
    )