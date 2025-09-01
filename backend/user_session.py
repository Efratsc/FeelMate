"""
User Session Management for FeelMate Chatbot
Handles user authentication, session validation, and user-specific data
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class UserSessionManager:
    """Manages user sessions and authentication for the chatbot"""
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
    
    def _get_connection(self):
        """Get PostgreSQL connection"""
        try:
            connection = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            return connection
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def validate_user_session(self, user_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate user session and return user info
        
        Args:
            user_id: User ID from authentication
            session_id: Optional session ID to validate
            
        Returns:
            Dict with user info and session validation status
        """
        conn = self._get_connection()
        if not conn:
            return {"valid": False, "error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            # Check if user exists in the user table (from better-auth)
            cursor.execute("""
                SELECT id, email, "createdAt" 
                FROM "user" 
                WHERE id = %s
            """, (user_id,))
            
            user_result = cursor.fetchone()
            if not user_result:
                return {"valid": False, "error": "User not found"}
            
            user_info = {
                "user_id": user_result['id'],
                "email": user_result['email'],
                "created_at": user_result['createdAt'].isoformat() if user_result['createdAt'] else None
            }
            
            # If session_id provided, validate it belongs to this user
            if session_id:
                cursor.execute("""
                    SELECT session_id, user_id, created_at, last_activity, is_active
                    FROM chat_sessions 
                    WHERE session_id = %s AND user_id = %s
                """, (session_id, user_id))
                
                session_result = cursor.fetchone()
                if not session_result:
                    return {
                        "valid": False, 
                        "error": "Session not found or doesn't belong to user",
                        "user_info": user_info
                    }
                
                # Check if session is still active (not expired)
                if not session_result['is_active']:
                    return {
                        "valid": False, 
                        "error": "Session has expired",
                        "user_info": user_info
                    }
                
                user_info["session_id"] = session_id
                user_info["session_active"] = True
            
            cursor.close()
            return {"valid": True, "user_info": user_info}
            
        except Exception as e:
            print(f"Error validating user session: {e}")
            return {"valid": False, "error": str(e)}
        finally:
            conn.close()
    
    def get_user_chat_history(self, user_id: str, limit: int = 50) -> list:
        """
        Get user's recent chat sessions and messages
        
        Args:
            user_id: User ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of chat sessions with recent messages
        """
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # Get recent chat sessions for user
            cursor.execute("""
                SELECT cs.session_id, cs.created_at, cs.last_activity, cs.current_emotion, cs.severity_level,
                       COUNT(cm.id) as message_count
                FROM chat_sessions cs
                LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
                WHERE cs.user_id = %s AND cs.is_active = TRUE
                GROUP BY cs.session_id, cs.created_at, cs.last_activity, cs.current_emotion, cs.severity_level
                ORDER BY cs.last_activity DESC
                LIMIT %s
            """, (user_id, limit))
            
            sessions = []
            for row in cursor.fetchall():
                session_info = {
                    "session_id": row['session_id'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                    "last_activity": row['last_activity'].isoformat() if row['last_activity'] else None,
                    "current_emotion": row['current_emotion'],
                    "severity_level": row['severity_level'],
                    "message_count": row['message_count']
                }
                
                # Get recent messages for this session
                cursor.execute("""
                    SELECT message, sender, emotion, timestamp
                    FROM chat_messages
                    WHERE session_id = %s
                    ORDER BY timestamp DESC
                    LIMIT 5
                """, (row['session_id'],))
                
                recent_messages = []
                for msg_row in cursor.fetchall():
                    recent_messages.append({
                        "message": msg_row['message'],
                        "sender": msg_row['sender'],
                        "emotion": msg_row['emotion'],
                        "timestamp": msg_row['timestamp'].isoformat() if msg_row['timestamp'] else None
                    })
                
                session_info["recent_messages"] = recent_messages
                sessions.append(session_info)
            
            cursor.close()
            return sessions
            
        except Exception as e:
            print(f"Error getting user chat history: {e}")
            return []
        finally:
            conn.close()
    
    def cleanup_user_sessions(self, user_id: str, timeout_hours: int = 24) -> int:
        """
        Clean up expired sessions for a specific user
        
        Args:
            user_id: User ID
            timeout_hours: Hours after which sessions are considered expired
            
        Returns:
            Number of sessions cleaned up
        """
        conn = self._get_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            
            # Mark old sessions as inactive
            cursor.execute("""
                UPDATE chat_sessions 
                SET is_active = FALSE 
                WHERE user_id = %s 
                AND last_activity < NOW() - INTERVAL '%s hours'
                AND is_active = TRUE
            """, (user_id, timeout_hours))
            
            cleaned_count = cursor.rowcount
            conn.commit()
            cursor.close()
            
            return cleaned_count
            
        except Exception as e:
            print(f"Error cleaning up user sessions: {e}")
            return 0
        finally:
            conn.close()

# Global instance
user_session_manager = UserSessionManager()

def get_user_session_manager():
    """Get the global user session manager instance"""
    return user_session_manager
