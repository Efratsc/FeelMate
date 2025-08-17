from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import psycopg2
import psycopg2.extras
import os
from datetime import datetime
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="FeelMate API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("DATABASE_URL not found in environment variables")
            return None
        
        connection = psycopg2.connect(database_url)
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Create chat tables if they don't exist
def init_chat_tables():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Create chat_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    current_emotion TEXT,
                    severity_level TEXT,
                    conversation_context TEXT
                )
            """)
            
            # Create chat_messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    emotion TEXT,
                    severity TEXT,
                    confidence FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("Chat tables initialized successfully")
        except Exception as e:
            print(f"Error initializing tables: {e}")

# Initialize tables on startup
init_chat_tables()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    emotion: str
    severity: str
    confidence: float
    needs_help: bool
    resources: List[Dict]
    session_id: str

# Emotion classification with context
class ContextAwareEmotionClassifier:
    def __init__(self):
        self.emotion_keywords = {
            'sad': ['sad', 'depressed', 'unhappy', 'miserable', 'hopeless', 'lonely', 'empty', 'worthless'],
            'anxious': ['anxious', 'worried', 'nervous', 'stressed', 'panic', 'fear', 'scared', 'overwhelmed'],
            'angry': ['angry', 'furious', 'mad', 'irritated', 'frustrated', 'rage', 'hate', 'bitter'],
            'happy': ['happy', 'joyful', 'excited', 'elated', 'content', 'pleased', 'grateful', 'blessed'],
            'confused': ['confused', 'lost', 'uncertain', 'unsure', 'doubtful', 'questioning', 'perplexed'],
            'crisis': ['suicide', 'kill myself', 'end it all', 'no reason to live', 'better off dead', 'hurt myself', 'self-harm']
        }
    
    def classify_emotion_with_context(self, message: str, conversation_history: List[str]) -> Dict:
        # Combine current message with recent history for context
        full_context = " ".join(conversation_history[-3:] + [message]).lower()
        
        # Check for crisis indicators first
        if any(keyword in full_context for keyword in self.emotion_keywords['crisis']):
            return {
                'emotion': 'crisis',
                'severity': 'critical',
                'confidence': 0.95,
                'needs_help': True
            }
        
        # Analyze emotion patterns
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            if emotion != 'crisis':
                score = sum(1 for keyword in keywords if keyword in full_context)
                if score > 0:
                    emotion_scores[emotion] = score
        
        if emotion_scores:
            # Get the emotion with highest score
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            score = emotion_scores[primary_emotion]
            
            # Determine severity based on intensity and context
            severity = 'moderate'
            if score >= 3 or any(word in message.lower() for word in ['very', 'extremely', 'terribly']):
                severity = 'high'
            elif score == 1 and len(conversation_history) < 2:
                severity = 'low'
            
            return {
                'emotion': primary_emotion,
                'severity': severity,
                'confidence': min(0.9, 0.3 + (score * 0.2)),
                'needs_help': severity in ['high', 'critical']
            }
        
        # Default classification
        return {
            'emotion': 'neutral',
            'severity': 'low',
            'confidence': 0.5,
            'needs_help': False
        }

# Response generator with context awareness
class ContextAwareResponseGenerator:
    def __init__(self):
        self.emotion_responses = {
            'sad': {
                'low': "I hear that you're feeling down. Would you like to talk more about what's on your mind?",
                'moderate': "It sounds like you're going through a difficult time. I'm here to listen. Can you tell me more about what's making you feel this way?",
                'high': "I can sense that you're really struggling right now. Your feelings are valid, and it's okay to not be okay. Would you like to share more about what's happening?"
            },
            'anxious': {
                'low': "I notice you seem a bit anxious. Is there something specific that's worrying you?",
                'moderate': "Anxiety can be really overwhelming. Let's take a moment to breathe together. What's causing you to feel this way?",
                'high': "I can see that anxiety is really affecting you right now. Remember, you're safe here. Can you tell me what's making you feel so anxious?"
            },
            'angry': {
                'low': "I can sense some frustration. What's been bothering you lately?",
                'moderate': "It sounds like you're dealing with some anger. That's a natural emotion. Would you like to talk about what happened?",
                'high': "I can feel the intensity of your emotions. It's okay to be angry. Can you help me understand what led to this?"
            },
            'crisis': {
                'critical': "I'm very concerned about what you're saying. You're not alone, and there are people who want to help you. Please call the National Suicide Prevention Lifeline at 988 or text HOME to 741741 to reach the Crisis Text Line. These services are free, confidential, and available 24/7."
            }
        }
    
    def generate_response(self, emotion_data: Dict, conversation_history: List[str], user_message: str) -> str:
        emotion = emotion_data['emotion']
        severity = emotion_data['severity']
        
        # Check if this is a follow-up question
        if len(conversation_history) > 0:
            last_ai_message = conversation_history[-1] if conversation_history[-1].startswith("AI:") else None
            
            # If user is responding to a question, acknowledge their response
            if last_ai_message and any(word in last_ai_message.lower() for word in ['tell me', 'share', 'what', 'how', 'why']):
                if emotion == 'crisis':
                    return self.emotion_responses['crisis']['critical']
                else:
                    base_response = self.emotion_responses.get(emotion, {}).get(severity, "Thank you for sharing that with me. I'm here to listen.")
                    return f"Thank you for opening up about that. {base_response}"
        
        # Generate appropriate response based on emotion and severity
        if emotion == 'crisis':
            return self.emotion_responses['crisis']['critical']
        
        response = self.emotion_responses.get(emotion, {}).get(severity, "I'm here to listen. Would you like to tell me more?")
        return response
    
    def get_resources(self, emotion_data: Dict) -> List[Dict]:
        if emotion_data['needs_help']:
            return [
                {
                    "title": "Crisis Resources",
                    "description": "24/7 support available",
                    "url": "https://988lifeline.org/",
                    "type": "crisis"
                },
                {
                    "title": "Find a Therapist",
                    "description": "Professional mental health support",
                    "url": "https://www.psychologytoday.com/us/therapists",
                    "type": "therapy"
                }
            ]
        return []

# Initialize classifiers
emotion_classifier = ContextAwareEmotionClassifier()
response_generator = ContextAwareResponseGenerator()

# Database operations
def get_or_create_session(user_id: str, session_id: Optional[str] = None) -> str:
    conn = get_db_connection()
    if not conn:
        return f"session-{user_id}-{datetime.now().timestamp()}"
    
    try:
        cursor = conn.cursor()
        
        if session_id:
            # Check if session exists
            cursor.execute("SELECT session_id FROM chat_sessions WHERE session_id = %s", (session_id,))
            if cursor.fetchone():
                return session_id
        
        # Create new session
        new_session_id = f"session-{user_id}-{datetime.now().timestamp()}"
        cursor.execute("""
            INSERT INTO chat_sessions (user_id, session_id, created_at, updated_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (user_id, new_session_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return new_session_id
    except Exception as e:
        print(f"Error in get_or_create_session: {e}")
        return f"session-{user_id}-{datetime.now().timestamp()}"

def save_message(session_id: str, message: str, sender: str, emotion_data: Dict):
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (session_id, message, sender, emotion, severity, confidence, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (
            session_id, 
            message, 
            sender, 
            emotion_data.get('emotion'), 
            emotion_data.get('severity'), 
            emotion_data.get('confidence', 0.0)
        ))
        
        # Update session with current emotion
        cursor.execute("""
            UPDATE chat_sessions 
            SET current_emotion = %s, severity_level = %s, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = %s
        """, (emotion_data.get('emotion'), emotion_data.get('severity'), session_id))
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error saving message: {e}")

def get_conversation_history(session_id: str) -> List[str]:
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT message, sender FROM chat_messages 
            WHERE session_id = %s 
            ORDER BY timestamp ASC
        """, (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            message, sender = row
            messages.append(f"{sender}: {message}")
        
        cursor.close()
        conn.close()
        return messages
    except Exception as e:
        print(f"Error getting conversation history: {e}")
        return []

# API endpoints
@app.get("/")
def read_root():
    return {"message": "FeelMate Emotional Support API with Chat History"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected" if get_db_connection() else "disconnected"}

@app.post("/api/chat/send-message")
async def send_message(chat_message: ChatMessage):
    try:
        # Get or create session
        session_id = get_or_create_session(chat_message.user_id, chat_message.session_id)
        
        # Get conversation history
        conversation_history = get_conversation_history(session_id)
        
        # Classify emotion with context
        emotion_data = emotion_classifier.classify_emotion_with_context(
            chat_message.message, 
            conversation_history
        )
        
        # Generate response with context
        ai_response = response_generator.generate_response(
            emotion_data, 
            conversation_history, 
            chat_message.message
        )
        
        # Save user message
        save_message(session_id, chat_message.message, "user", emotion_data)
        
        # Save AI response
        save_message(session_id, ai_response, "ai", {
            'emotion': 'supportive',
            'severity': 'low',
            'confidence': 0.8
        })
        
        # Get resources if needed
        resources = response_generator.get_resources(emotion_data)
        
        return ChatResponse(
            response=ai_response,
            emotion=emotion_data['emotion'],
            severity=emotion_data['severity'],
            confidence=emotion_data['confidence'],
            needs_help=emotion_data['needs_help'],
            resources=resources,
            session_id=session_id
        )
        
    except Exception as e:
        print(f"Error in send_message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT message, sender, emotion, severity, timestamp 
            FROM chat_messages 
            WHERE session_id = %s 
            ORDER BY timestamp ASC
        """, (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            message, sender, emotion, severity, timestamp = row
            messages.append({
                "message": message,
                "sender": sender,
                "emotion": emotion,
                "severity": severity,
                "timestamp": timestamp.isoformat()
            })
        
        cursor.close()
        conn.close()
        
        return {"messages": messages, "session_id": session_id}
        
    except Exception as e:
        print(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/analytics/dashboard-stats")
async def get_dashboard_stats():
    try:
        conn = get_db_connection()
        if not conn:
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "emotion_distribution": {},
                "severity_distribution": {}
            }
        
        cursor = conn.cursor()
        
        # Get total sessions
        cursor.execute("SELECT COUNT(*) FROM chat_sessions")
        total_sessions = cursor.fetchone()[0]
        
        # Get total messages
        cursor.execute("SELECT COUNT(*) FROM chat_messages")
        total_messages = cursor.fetchone()[0]
        
        # Get emotion distribution
        cursor.execute("""
            SELECT emotion, COUNT(*) 
            FROM chat_messages 
            WHERE emotion IS NOT NULL 
            GROUP BY emotion
        """)
        emotion_distribution = dict(cursor.fetchall())
        
        # Get severity distribution
        cursor.execute("""
            SELECT severity, COUNT(*) 
            FROM chat_messages 
            WHERE severity IS NOT NULL 
            GROUP BY severity
        """)
        severity_distribution = dict(cursor.fetchall())
        
        cursor.close()
        conn.close()
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "emotion_distribution": emotion_distribution,
            "severity_distribution": severity_distribution
        }
        
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return {
            "total_sessions": 0,
            "total_messages": 0,
            "emotion_distribution": {},
            "severity_distribution": {}
        }

if __name__ == "__main__":
    print("Starting FeelMate API server with chat history...")
    print("API will be available at: http://localhost:8001")
    print("Health check: http://localhost:8001/health")
    print("API docs: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)
