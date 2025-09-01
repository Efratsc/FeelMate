"""
Production FastAPI server for FeelMate Emotion-Aware Chatbot
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import LangGraph pipeline
from app.ml.graph_pipeline import get_graph

# Import configuration
from config import FRONTEND_URLS, HOST, PORT, RELOAD, LOG_LEVEL

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FeelMate API",
    description="AI-powered emotional support chatbot with emotion detection",
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

# Initialize LangGraph
graph = get_graph()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    emotion: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[float] = None
    needs_help: Optional[bool] = None
    resources: Optional[list] = None
    session_id: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FeelMate API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FeelMate API - AI-powered emotional support chatbot",
        "version": "1.0.0",
        "features": [
            "Emotion detection using HuggingFace models",
            "LLM-free LangGraph conversation pipeline",
            "Crisis detection and intervention",
            "Personalized contextual responses",
            "Real-time streaming chat interface"
        ],
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

# Main chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to the FeelMate chatbot"""
    try:
        # Validate input
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Process message through LangGraph pipeline
        result = graph.run({
            "message": request.message,
            "session_id": request.session_id or "default"
        })
        
        # Return response with metadata
        return ChatResponse(
            response=result.response,
            emotion=result.emotion,
            severity=result.severity,
            confidence=result.confidence,
            needs_help=result.needs_help,
            resources=result.resources,
            session_id=result.session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get conversation history for a session
@app.get("/api/chat/history/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a specific session"""
    try:
        history = graph.get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "message_count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

# Clear conversation history for a session
@app.delete("/api/chat/history/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a specific session"""
    try:
        graph.clear_conversation(session_id)
        return {
            "message": f"Conversation history cleared for session {session_id}",
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation history: {str(e)}")

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    logger.info("🚀 Starting FeelMate Emotion-Aware Chatbot...")
    logger.info("🧠 AI Mode: LangGraph (LLM-free)")
    logger.info(f"📍 Server will be available at: http://{HOST}:{PORT}")
    logger.info(f"📚 API documentation: http://{HOST}:{PORT}/docs")
    logger.info(f"🏥 Health check: http://{HOST}:{PORT}/health")
    
    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level=LOG_LEVEL.lower()
    )
