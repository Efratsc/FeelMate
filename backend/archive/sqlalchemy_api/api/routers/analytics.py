from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db, ChatSession, ChatMessage
from datetime import datetime, timedelta
from typing import List, Dict

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/user-patterns/{user_id}")
async def get_user_patterns(user_id: str, db: Session = Depends(get_db)):
    # Get user sessions
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    
    # Calculate patterns
    emotion_counts = {}
    total_messages = 0
    total_sessions = len(sessions)
    
    for session in sessions:
        messages = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).all()
        total_messages += len(messages)
        
        if session.dominant_emotion:
            emotion_counts[session.dominant_emotion] = emotion_counts.get(session.dominant_emotion, 0) + 1
    
    # Get recent activity
    recent_sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id,
        ChatSession.session_start >= datetime.utcnow() - timedelta(days=7)
    ).all()
    
    return {
        "user_id": user_id,
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "emotion_distribution": emotion_counts,
        "recent_sessions": len(recent_sessions),
        "average_session_length": total_messages / total_sessions if total_sessions > 0 else 0
    }

@router.get("/dashboard-stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    # Overall statistics
    total_sessions = db.query(ChatSession).count()
    total_messages = db.query(ChatMessage).count()
    
    # Today stats
    today = datetime.utcnow().date()
    today_sessions = db.query(ChatSession).filter(
        ChatSession.session_start >= today
    ).count()
    
    today_messages = db.query(ChatMessage).filter(
        ChatMessage.created_at >= today
    ).count()
    
    # Crisis detection
    crisis_messages = db.query(ChatMessage).filter(
        ChatMessage.emotion_detected == "crisis"
    ).count()
    
    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "today_sessions": today_sessions,
        "today_messages": today_messages,
        "crisis_detections": crisis_messages
    }
