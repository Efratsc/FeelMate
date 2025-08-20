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
            
            # Create chat_sessions table with session timeout
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    current_emotion TEXT,
                    severity_level TEXT,
                    conversation_context TEXT,
                    is_active BOOLEAN DEFAULT TRUE
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

# Session timeout configuration (in minutes)
SESSION_TIMEOUT_MINUTES = 30  # 30 minutes of inactivity

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Mark sessions as inactive if they haven't been updated in SESSION_TIMEOUT_MINUTES
        cursor.execute("""
            UPDATE chat_sessions 
            SET is_active = FALSE 
            WHERE last_activity < NOW() - INTERVAL '%s minutes'
            AND is_active = TRUE
        """, (SESSION_TIMEOUT_MINUTES,))
        
        # Delete messages from expired sessions (optional - for data cleanup)
        cursor.execute("""
            DELETE FROM chat_messages 
            WHERE session_id IN (
                SELECT session_id FROM chat_sessions 
                WHERE is_active = FALSE 
                AND last_activity < NOW() - INTERVAL '%s hours'
            )
        """, (24,))  # Delete messages from sessions inactive for 24+ hours
        
        # Delete very old inactive sessions
        cursor.execute("""
            DELETE FROM chat_sessions 
            WHERE is_active = FALSE 
            AND last_activity < NOW() - INTERVAL '%s hours'
        """, (24,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Session cleanup completed - timeout: {SESSION_TIMEOUT_MINUTES} minutes")
    except Exception as e:
        print(f"Error cleaning up sessions: {e}")

def update_session_activity(session_id: str):
    """Update session's last activity timestamp"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chat_sessions 
            SET last_activity = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = %s
        """, (session_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error updating session activity: {e}")

def get_or_create_session(user_id: str, session_id: Optional[str] = None) -> str:
    conn = get_db_connection()
    if not conn:
        return f"session-{user_id}-{datetime.now().timestamp()}"
    
    try:
        cursor = conn.cursor()
        
        # Clean up expired sessions first
        cleanup_expired_sessions()
        
        if session_id:
            # Check if session exists and is active
            cursor.execute("""
                SELECT session_id FROM chat_sessions 
                WHERE session_id = %s AND is_active = TRUE
            """, (session_id,))
            if cursor.fetchone():
                # Update activity timestamp
                update_session_activity(session_id)
                return session_id
        
        # Create new session
        new_session_id = f"session-{user_id}-{datetime.now().timestamp()}"
        cursor.execute("""
            INSERT INTO chat_sessions (user_id, session_id, created_at, updated_at, last_activity)
            VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
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
        
        # Update session with current emotion and activity
        cursor.execute("""
            UPDATE chat_sessions 
            SET current_emotion = %s, severity_level = %s, updated_at = CURRENT_TIMESTAMP, last_activity = CURRENT_TIMESTAMP
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
            SELECT message, sender, emotion, severity FROM chat_messages 
            WHERE session_id = %s 
            ORDER BY timestamp ASC
        """, (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            message, sender, emotion, severity = row
            # Include emotion context in the message format for better AI understanding
            if sender == "user":
                messages.append(f"user: {message}")
            else:
                messages.append(f"ai: {message}")
        
        cursor.close()
        conn.close()
        return messages
    except Exception as e:
        print(f"Error getting conversation history: {e}")
        return []

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
            'sad': ['sad', 'depressed', 'unhappy', 'miserable', 'hopeless', 'lonely', 'empty', 'worthless', 'down', 'blue', 'melancholy'],
            'anxious': ['anxious', 'worried', 'nervous', 'stressed', 'panic', 'fear', 'scared', 'overwhelmed', 'tense', 'jittery', 'uneasy'],
            'angry': ['angry', 'furious', 'mad', 'irritated', 'frustrated', 'rage', 'hate', 'bitter', 'annoyed', 'upset', 'livid'],
            'happy': ['happy', 'joyful', 'excited', 'elated', 'content', 'pleased', 'grateful', 'blessed', 'good', 'fine', 'okay', 'normal'],
            'confused': ['confused', 'lost', 'uncertain', 'unsure', 'doubtful', 'questioning', 'perplexed', 'mixed'],
            'crisis': ['suicide', 'kill myself', 'end it all', 'no reason to live', 'better off dead', 'hurt myself', 'self-harm', 'want to die', 'end my life', 'give up', 'cant take it anymore']
        }
    
    def classify_emotion_with_context(self, message: str, conversation_history: List[str]) -> Dict:
        # Get full conversation context (last 10 messages for better context)
        recent_messages = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        
        # Combine all recent messages with current message for full context
        full_context = " ".join(recent_messages + [message]).lower()
        current_message_lower = message.lower()
        
        # CRITICAL: Check for crisis indicators in CURRENT MESSAGE ONLY
        crisis_phrases = [
            'kill myself', 'kill my self', 'want to die', 'end my life', 'end it all',
            'no reason to live', 'better off dead', 'hurt myself', 'self harm',
            'suicide', 'give up', 'cant take it anymore', 'wanna kill', 'want to kill'
        ]
        
        # Check ONLY the current message for crisis indicators
        if any(phrase in current_message_lower for phrase in crisis_phrases):
            return {
                'emotion': 'crisis',
                'severity': 'critical',
                'confidence': 0.98,
                'needs_help': True
            }
        
        # Analyze emotional progression and patterns
        emotion_scores = {}
        emotion_history = []
        
        # Analyze each recent message for emotions (excluding crisis phrases)
        for msg in recent_messages:
            msg_lower = msg.lower()
            # Skip crisis phrases in history analysis to avoid false positives
            if any(phrase in msg_lower for phrase in crisis_phrases):
                continue
                
            for emotion, keywords in self.emotion_keywords.items():
                if emotion != 'crisis':
                    score = sum(1 for keyword in keywords if keyword in msg_lower)
                    if score > 0:
                        emotion_history.append(emotion)
                        emotion_scores[emotion] = emotion_scores.get(emotion, 0) + score
        
        # Analyze current message specifically (excluding crisis phrases)
        current_emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            if emotion != 'crisis':
                score = sum(1 for keyword in keywords if keyword in current_message_lower)
                if score > 0:
                    current_emotion_scores[emotion] = score
                    emotion_scores[emotion] = emotion_scores.get(emotion, 0) + (score * 2)  # Give more weight to current message
        
        # Determine primary emotion
        if emotion_scores:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            total_score = emotion_scores[primary_emotion]
            
            # Check for emotional escalation
            severity = 'low'
            if total_score >= 5 or any(word in current_message_lower for word in ['very', 'extremely', 'terribly', 'really']):
                severity = 'high'
            elif total_score >= 3:
                severity = 'moderate'
            
            # Check for emotional progression (e.g., from sad to crisis)
            if len(emotion_history) >= 2:
                recent_emotions = emotion_history[-3:]
                if 'sad' in recent_emotions and primary_emotion == 'sad' and total_score >= 4:
                    severity = 'high'  # Escalating sadness
            
            confidence = min(0.95, 0.4 + (total_score * 0.15))
            
            return {
                'emotion': primary_emotion,
                'severity': severity,
                'confidence': confidence,
                'needs_help': severity in ['high', 'critical'] or primary_emotion in ['sad', 'anxious']
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
                'critical': "I'm very concerned about what you're saying. You're not alone, and there are people who want to help you. Please call the National Suicide Prevention Lifeline at 988 or text HOME to 741741 to reach the Crisis Text Line. These services are free, confidential, and available 24/7. Your life has value, and there are people who care about you."
            }
        }
    
    def generate_response(self, emotion_data: Dict, conversation_history: List[str], user_message: str) -> str:
        emotion = emotion_data['emotion']
        severity = emotion_data['severity']
        
        # CRITICAL: Crisis responses take absolute priority for CURRENT message only
        if emotion == 'crisis':
            return self.emotion_responses['crisis']['critical']
        
        # Analyze conversation context for better responses
        recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        user_messages = [msg for msg in recent_messages if msg.startswith("user:")]
        ai_messages = [msg for msg in recent_messages if msg.startswith("ai:")]
        
        # Check if this is a follow-up to a previous question
        if ai_messages:
            last_ai_message = ai_messages[-1].replace("ai: ", "")
            
            # If AI asked a question and user is responding
            if any(word in last_ai_message.lower() for word in ['tell me', 'share', 'what', 'how', 'why', 'can you']):
                if emotion == 'sad' and severity in ['moderate', 'high']:
                    return "Thank you for opening up about that. I can hear how much this is affecting you. It's important to acknowledge these feelings. Would you like to talk more about what's been happening?"
                elif emotion == 'anxious':
                    return "Thank you for sharing that with me. Anxiety can feel overwhelming, and it's brave of you to talk about it. What do you think might help you feel a bit calmer right now?"
                elif emotion == 'angry':
                    return "I appreciate you telling me about this. Anger is a natural response to difficult situations. How are you feeling now that you've shared this?"
                elif emotion == 'happy':
                    return "That's wonderful to hear! I'm glad you're feeling better. What helped you get to this positive place?"
                else:
                    return "Thank you for sharing that with me. I'm here to listen. How are you feeling about this situation?"
        
        # Check for emotional escalation patterns (but don't maintain crisis state)
        if len(user_messages) >= 2:
            # Look for progression from neutral/sad to crisis indicators
            recent_user_content = " ".join([msg.replace("user: ", "") for msg in user_messages[-3:]])
            if any(word in recent_user_content.lower() for word in ['hopeless', 'worthless', 'alone', 'no point', 'tired']):
                if emotion == 'sad':
                    return "I'm noticing that you've been expressing some really difficult feelings. It sounds like you're going through a very tough time. You don't have to go through this alone. Would you like to talk more about what's been happening?"
        
        # Check if user is repeating themselves or seems stuck
        if len(user_messages) >= 3:
            recent_content = [msg.replace("user: ", "").lower() for msg in user_messages[-3:]]
            if len(set(recent_content)) <= 1:  # Same or very similar messages
                return "I notice you've been expressing similar feelings. It seems like you might be feeling stuck or overwhelmed. Sometimes talking about the root cause can help. What do you think is at the heart of these feelings?"
        
        # Generate appropriate response based on emotion and severity
        response = self.emotion_responses.get(emotion, {}).get(severity, "I'm here to listen. Would you like to tell me more?")
        
        # Add context-specific elements
        if emotion == 'sad' and severity == 'high':
            response += " Remember, it's okay to not be okay, and your feelings are valid."
        elif emotion == 'anxious' and severity == 'high':
            response += " Let's take this one step at a time."
        elif emotion == 'happy':
            response = "That's great to hear! I'm glad you're feeling positive. What's been going well for you?"
        
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

@app.get("/api/chat/session-status/{session_id}")
async def get_session_status(session_id: str):
    """Get session status and timeout information"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT is_active, last_activity, created_at 
            FROM chat_sessions 
            WHERE session_id = %s
        """, (session_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            return {"active": False, "message": "Session not found"}
        
        is_active, last_activity, created_at = result
        
        # Calculate time until timeout
        from datetime import datetime, timedelta
        now = datetime.now()
        last_activity_dt = last_activity if isinstance(last_activity, datetime) else datetime.fromisoformat(str(last_activity))
        time_since_activity = now - last_activity_dt
        minutes_until_timeout = SESSION_TIMEOUT_MINUTES - (time_since_activity.total_seconds() / 60)
        
        return {
            "active": is_active,
            "last_activity": last_activity.isoformat() if last_activity else None,
            "created_at": created_at.isoformat() if created_at else None,
            "minutes_until_timeout": max(0, int(minutes_until_timeout)),
            "session_timeout_minutes": SESSION_TIMEOUT_MINUTES
        }
        
    except Exception as e:
        print(f"Error getting session status: {e}")
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
