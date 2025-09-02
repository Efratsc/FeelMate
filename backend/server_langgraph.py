"""
Production FastAPI server for FeelMate with LLM-free LangGraph and PostgreSQL
"""

import logging
import uvicorn
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.ml.graph_pipeline import get_graph, GraphResult
from config import FRONTEND_URLS, HOST, PORT, RELOAD, LOG_LEVEL, DATABASE_URL
try:
    from app.auth.neon_auth import NeonAuth
    AUTH_AVAILABLE = True
except Exception as _auth_err:
    NeonAuth = None  # type: ignore
    AUTH_AVAILABLE = False

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="FeelMate Emotion-Aware Chatbot",
    description="LLM-free LangGraph with PostgreSQL authentication",
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

# Initialize components
graph = get_graph()
auth_manager = None
if AUTH_AVAILABLE and DATABASE_URL:
    try:
        auth_manager = NeonAuth()
        logging.info("✅ PostgreSQL auth initialized")
    except Exception as e:
        logging.warning(f"⚠️  Auth disabled: {e}")
else:
    logging.warning("⚠️  Auth disabled (missing DATABASE_URL or NeonAuth)")

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SignUpRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class SignInRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting FeelMate LLM-free LangGraph Server...")
    logger.info("✅ Server ready to accept requests")
    logger.info("🧠 Using LLM-free LangGraph pipeline")
    logger.info("🗄️ PostgreSQL authentication active")

@app.get("/")
async def root():
    return {
        "message": "FeelMate LLM-free LangGraph API",
        "version": "1.0.0",
        "status": "production",
        "features": [
            "LLM-free LangGraph pipeline",
            "PostgreSQL authentication",
            "Emotion detection (HuggingFace)",
            "Crisis detection",
            "Contextual responses",
            "Resource recommendations"
        ],
        "endpoints": {
            "/api/chat/send-message": "POST - Send a message and get response",
            "/api/auth/sign-up": "POST - User registration",
            "/api/auth/sign-in": "POST - User login",
            "/api/auth/user/{email}": "GET - Get user info",
            "/api/chat/history/{session_id}": "GET - Get conversation history",
            "/api/chat/clear/{session_id}": "POST - Clear conversation history",
            "/health": "GET - Check server health",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FeelMate LLM-free LangGraph",
        "model": "HuggingFace emotion detection + rule-based responses",
        "version": "1.0.0"
    }

@app.post("/api/chat/send-message")
async def send_message(request: ChatRequest, user_id: str = "default_user"):
    """
    Main chat endpoint using LLM-free LangGraph
    """
    try:
        logger.info(f"Chat request from user: {user_id}")
        
        # Process with LangGraph
        result: GraphResult = graph.run(
            user_text=request.message,
            user_id=user_id,
            session_id=request.session_id
        )

        return {
            "response": result.response,
            "emotion": result.emotion,
            "severity": result.severity,
            "crisis_detected": result.crisis_detected,
            "session_id": result.session_id,
            "confidence": result.confidence,
            "needs_help": result.needs_help,
            "resources": result.resources or []
        }

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/auth/sign-up", response_model=AuthResponse)
async def sign_up(request: SignUpRequest):
    """User registration"""
    try:
        if not auth_manager:
            return AuthResponse(success=False, message="Auth is disabled: set DATABASE_URL")
        data = auth_manager.sign_up(request.email, request.password, request.name or "")
        user_id = data["user"]["id"]
        session_id = auth_manager.create_session(user_id)
        
        return AuthResponse(
            success=True,
            message="User registered successfully",
            user_id=user_id,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Sign up error: {e}")
        return AuthResponse(
            success=False,
            message=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/sign-in", response_model=AuthResponse)
async def sign_in(request: SignInRequest):
    """User login"""
    try:
        if not auth_manager:
            return AuthResponse(success=False, message="Auth is disabled: set DATABASE_URL")
        data = auth_manager.sign_in(request.email, request.password)
        user_id = data["user"]["id"]
        session_id = auth_manager.create_session(user_id)
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user_id=user_id,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Sign in error: {e}")
        return AuthResponse(
            success=False,
            message=f"Login failed: {str(e)}"
        )

@app.get("/api/auth/user/{email}")
async def get_user(email: str):
    """Get user information"""
    try:
        if not auth_manager:
            raise HTTPException(status_code=503, detail="Auth is disabled: set DATABASE_URL")
        user = auth_manager.get_user(email)
        return {
            "user_id": user["id"],
            "email": user["email"],
            "name": user.get("name"),
            "created_at": user.get("created_at")
        }
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/chat/history/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = graph.get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "messages": history
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation history")

@app.post("/api/chat/clear/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session"""
    try:
        graph.clear_conversation(session_id)
        return {"message": "Conversation history cleared", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear conversation history")

if __name__ == "__main__":
    # Check if DATABASE_URL is set
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL environment variable is required")
        logger.info("Please set DATABASE_URL in your environment or .env file")
        exit(1)
    
    uvicorn.run(
        "server_langgraph:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level=LOG_LEVEL
    )
