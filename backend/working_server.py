from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import joblib
import os

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
    """Emotion classification using trained ML model"""
    
    try:
        # Load the trained model
        model_path = "app/ml/models/emotion_classifier.pkl"
        vectorizer_path = "app/ml/models/vectorizer.pkl"
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            
            # Vectorize and predict
            X = vectorizer.transform([chat_message.message])
            emotion = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]
            confidence = max(probabilities)
            
            # Map emotions to severity
            severity_map = {
                "joy": 2, "neutral": 4, "surprise": 5, "fear": 6,
                "anger": 7, "sadness": 8, "disgust": 6
            }
            severity = severity_map.get(emotion, 4)
            needs_help = severity >= 6
            
            # Generate response
            responses = {
                "joy": "It's wonderful that you're feeling happy! What brought on these positive feelings?",
                "sadness": "I hear that you're feeling down, and your feelings are completely valid. Would you like to talk more?",
                "anger": "I understand you're feeling angry. It's important to acknowledge these feelings. What triggered this?",
                "fear": "Fear can be really overwhelming. Let's take a deep breath together. What's on your mind?",
                "surprise": "It sounds like something unexpected happened. How are you processing this?",
                "disgust": "I understand you're feeling disgusted. What triggered this reaction?",
                "neutral": "Thank you for sharing. I'm here to listen and support you."
            }
            response = responses.get(emotion, "I'm here to listen and support you.")
            
        else:
            # Fallback to keyword-based classification
            text = chat_message.message.lower()
            if any(word in text for word in ["happy", "joy", "excited"]):
                emotion, severity, response = "joy", 2, "It's wonderful that you're feeling happy!"
            elif any(word in text for word in ["sad", "depressed", "hopeless"]):
                emotion, severity, response = "sadness", 8, "I hear that you're feeling down. Your feelings are valid."
            elif any(word in text for word in ["angry", "mad", "furious"]):
                emotion, severity, response = "anger", 7, "I understand you're feeling angry. What triggered this?"
            elif any(word in text for word in ["scared", "afraid", "worried"]):
                emotion, severity, response = "fear", 6, "Fear can be overwhelming. Let's take a deep breath together."
            else:
                emotion, severity, response = "neutral", 4, "Thank you for sharing. I'm here to listen."
            
            confidence = 0.8
            needs_help = severity >= 6
        
        # Get resources
        resources = []
        if needs_help:
            resources = [
                {"name": "Psychology Today", "url": "https://www.psychologytoday.com/us/therapists"},
                {"name": "BetterHelp", "url": "https://www.betterhelp.com"}
            ]
        
        return {
            "response": response,
            "emotion": emotion,
            "severity": severity,
            "confidence": confidence,
            "needs_help": needs_help,
            "resources": resources,
            "session_id": chat_message.session_id or "test-session"
        }
        
    except Exception as e:
        return {
            "response": "I'm here to listen and support you. How are you feeling today?",
            "emotion": "neutral",
            "severity": 4,
            "confidence": 0.5,
            "needs_help": False,
            "resources": [],
            "session_id": chat_message.session_id or "test-session"
        }

if __name__ == "__main__":
    print("Starting FeelMate API server...")
    print("API will be available at: http://localhost:8001")
    print("Health check: http://localhost:8001/health")
    print("API docs: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)