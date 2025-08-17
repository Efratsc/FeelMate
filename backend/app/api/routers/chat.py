from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.database import get_db, ChatSession, ChatMessage
from app.services.emotion_classifier import EmotionClassifier
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["chat"])
emotion_classifier = EmotionClassifier()

class ChatMessageRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    emotion: str
    severity: int
    confidence: float
    needs_help: bool
    resources: List[dict]
    session_id: str

@router.post("/send-message", response_model=ChatResponse)
async def send_message(message: ChatMessageRequest, db: Session = Depends(get_db)):
    # Classify emotion
    emotion_data = emotion_classifier.classify_emotion(message.message)
    
    # Generate response
    ai_response = emotion_classifier.generate_response(emotion_data)
    
    # Get resources
    resources = emotion_classifier.get_resources(emotion_data)
    
    # Create or get session
    session_id = message.session_id or str(uuid.uuid4())
    
    # Store message in database
    chat_message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        message_text=message.message,
        sender_type="user",
        emotion_detected=emotion_data["emotion"],
        emotion_confidence=emotion_data["confidence"]
    )
    db.add(chat_message)
    
    # Store AI response
    ai_message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        message_text=ai_response,
        sender_type="ai",
        emotion_detected=emotion_data["emotion"],
        emotion_confidence=emotion_data["confidence"]
    )
    db.add(ai_message)
    
    # Update or create session
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        session = ChatSession(
            id=session_id,
            user_id=message.user_id,
            dominant_emotion=emotion_data["emotion"],
            emotion_severity=emotion_data["severity"]
        )
        db.add(session)
    else:
        session.dominant_emotion = emotion_data["emotion"]
        session.emotion_severity = emotion_data["severity"]
    
    db.commit()
    
    return ChatResponse(
        response=ai_response,
        emotion=emotion_data["emotion"],
        severity=emotion_data["severity"],
        confidence=emotion_data["confidence"],
        needs_help=emotion_data["needs_immediate_help"],
        resources=resources,
        session_id=session_id
    )

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()
    return {"messages": messages}

@router.post("/start-session")
async def start_session(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    session = ChatSession(
        id=session_id,
        user_id=user_id,
        session_start=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    return {"session_id": session_id}
