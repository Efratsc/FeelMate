from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

class ChatMessage(BaseModel):
    message: str
    user_id: str = None
    session_id: str = None

@app.get("/")
def read_root():
    return {"message": "FeelMate Emotional Support API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/chat/send-message")
async def send_message(chat_message: ChatMessage):
    """Simple emotion classification and response"""
    
    # Simple keyword-based emotion detection
    text = chat_message.message.lower()
    
    if any(word in text for word in ["happy", "joy", "excited", "great", "wonderful"]):
        emotion = "joy"
        severity = 2
        response = "It's wonderful that you're feeling happy! What brought on these positive feelings?"
    elif any(word in text for word in ["sad", "depressed", "hopeless", "worthless", "empty"]):
        emotion = "sadness"
        severity = 8
        response = "I hear that you're feeling down, and your feelings are completely valid. Would you like to talk more about what's causing these feelings?"
    elif any(word in text for word in ["angry", "mad", "furious", "hate", "irritated"]):
        emotion = "anger"
        severity = 7
        response = "I understand you're feeling angry. It's important to acknowledge these feelings. What triggered this anger?"
    elif any(word in text for word in ["scared", "afraid", "worried", "anxious", "nervous"]):
        emotion = "fear"
        severity = 6
        response = "Fear can be really overwhelming. Let's take a deep breath together. What specific thoughts are running through your mind?"
    elif any(word in text for word in ["suicide", "kill myself", "end it all"]):
        emotion = "crisis"
        severity = 10
        response = "I am very concerned about what you're sharing. Your life has immense value. Please call the National Suicide Prevention Lifeline at 988 immediately."
    else:
        emotion = "neutral"
        severity = 4
        response = "Thank you for sharing. I'm here to listen and support you. How are you feeling today?"
    
    needs_help = severity >= 6
    
    resources = []
    if needs_help:
        resources = [
            {"name": "Psychology Today", "url": "https://www.psychologytoday.com/us/therapists", "description": "Find therapists and psychiatrists"},
            {"name": "BetterHelp", "url": "https://www.betterhelp.com", "description": "Online therapy platform"}
        ]
    
    if emotion == "crisis":
        resources = [
            {"name": "National Suicide Prevention Lifeline", "phone": "988", "description": "24/7 crisis support"},
            {"name": "Crisis Text Line", "text": "HOME to 741741", "description": "24/7 crisis support via text"}
        ]
    
    return {
        "response": response,
        "emotion": emotion,
        "severity": severity,
        "confidence": 0.8,
        "needs_help": needs_help,
        "resources": resources,
        "session_id": chat_message.session_id or "test-session"
    }

@app.get("/api/analytics/dashboard-stats")
async def get_dashboard_stats():
    """Simple dashboard statistics"""
    return {
        "total_sessions": 100,
        "total_messages": 500,
        "today_sessions": 10,
        "today_messages": 25,
        "crisis_detections": 2
    }

if __name__ == "__main__":
    print("Starting FeelMate API server...")
    print("API will be available at: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

