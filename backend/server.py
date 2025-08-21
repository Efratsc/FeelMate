"""
Production FastAPI server for FeelMate Emotion-Aware Chatbot
CPU-only version with frontend integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging

# Import our production chatbot
from chatbot import get_chatbot, ChatMessage, ChatResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FeelMate Emotion-Aware Chatbot",
    description="Production-ready supportive chatbot that detects emotions and provides empathetic responses",
    version="1.0.0"
)

# Import configuration
from config import FRONTEND_URLS, DEBUG

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get production chatbot instance
chatbot = get_chatbot()

@app.on_event("startup")
async def startup_event():
    """Initialize chatbot on startup"""
    logger.info("🚀 Starting FeelMate Production Emotion-Aware Chatbot...")
    logger.info("✅ Server ready to accept requests")
    logger.info("💡 Using CPU-only emotion detection with intelligent response templates")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FeelMate Emotion-Aware Chatbot API",
        "version": "1.0.0",
        "status": "production",
        "features": [
            "CPU-only emotion detection",
            "Intelligent response templates",
            "Crisis detection",
            "Conversation memory",
            "Resource recommendations"
        ],
        "endpoints": {
            "/chat/invoke": "POST - Send a message and get response",
            "/api/chat/send-message": "POST - Frontend compatibility endpoint",
            "/health": "GET - Check server health",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FeelMate Production Chatbot",
        "model": "CPU-only emotion detection",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.post("/chat/invoke")
async def chat_invoke(request: ChatMessage) -> ChatResponse:
    """
    Main chat endpoint that processes user messages
    
    This endpoint:
    1. Detects emotion in the user's message using CPU-only inference
    2. Checks for crisis indicators
    3. Generates supportive responses using intelligent templates
    4. Maintains conversation memory
    5. Returns structured response with emotion data
    """
    try:
        logger.info(f"Processing message from user {request.user_id}")
        
        # Process the message through our production chatbot
        response = chatbot.chat(
            user_message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        logger.info(f"Generated response with emotion: {response.emotion}, severity: {response.severity}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Frontend compatibility endpoint
@app.post("/api/chat/send-message")
async def send_message(request: ChatMessage) -> ChatResponse:
    """
    Frontend compatibility endpoint
    Maps to the main /chat/invoke endpoint
    """
    return await chat_invoke(request)

if __name__ == "__main__":
    # Import configuration
    from config import HOST, PORT, RELOAD, LOG_LEVEL
    
    # Run the production server
    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,  # Match the port expected by your frontend
        reload=RELOAD,  # Use config for reload setting
        log_level=LOG_LEVEL
    )
