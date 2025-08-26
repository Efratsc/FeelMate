"""
Custom LangChain ChatMessageHistory implementation for PostgreSQL
Integrates with existing FeelMate database schema and connection patterns
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from dotenv import load_dotenv

load_dotenv()

class PostgresChatMessageHistory(BaseChatMessageHistory):
    """
    Custom LangChain ChatMessageHistory implementation using PostgreSQL
    Integrates with existing FeelMate chat_sessions and chat_messages tables
    """
    
    def __init__(self, session_id: str, user_id: str, max_messages: int = 10):
        """
        Initialize PostgreSQL-based chat message history
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier from authentication
            max_messages: Maximum number of messages to load from history
        """
        self.session_id = session_id
        self.user_id = user_id
        self.max_messages = max_messages
        self.db_url = os.getenv("DATABASE_URL")
        
        # Ensure session exists in database
        self._ensure_session_exists()
        
        # Load existing messages
        self._messages = self._load_messages()
    
    def _get_connection(self):
        """Get PostgreSQL connection with RealDictCursor"""
        try:
            connection = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            return connection
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def _ensure_session_exists(self):
        """Ensure chat session exists in database"""
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_sessions (user_id, session_id, created_at, updated_at, last_activity)
                VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (session_id) DO UPDATE SET
                    last_activity = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            """, (self.user_id, self.session_id))
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error ensuring session exists: {e}")
        finally:
            conn.close()
    
    def _load_messages(self) -> List[BaseMessage]:
        """Load existing messages from PostgreSQL"""
        conn = self._get_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message, sender, emotion, severity, timestamp
                FROM chat_messages
                WHERE session_id = %s
                ORDER BY timestamp ASC
                LIMIT %s
            """, (self.session_id, self.max_messages))
            
            messages = []
            for row in cursor.fetchall():
                if row['sender'] == 'user':
                    messages.append(HumanMessage(content=row['message']))
                elif row['sender'] == 'ai':
                    messages.append(AIMessage(content=row['message']))
                elif row['sender'] == 'system':
                    messages.append(SystemMessage(content=row['message']))
            
            cursor.close()
            return messages
        except Exception as e:
            print(f"Error loading messages: {e}")
            return []
        finally:
            conn.close()
    
    def add_user_message(self, message: str, emotion_data: Optional[Dict] = None) -> None:
        """Add a user message to the conversation history"""
        human_message = HumanMessage(content=message)
        self._messages.append(human_message)
        self._save_message_to_db('user', message, emotion_data)
    
    def add_ai_message(self, message: str, emotion_data: Optional[Dict] = None) -> None:
        """Add an AI message to the conversation history"""
        ai_message = AIMessage(content=message)
        self._messages.append(ai_message)
        self._save_message_to_db('ai', message, emotion_data)
    
    def add_system_message(self, message: str) -> None:
        """Add a system message to the conversation history"""
        system_message = SystemMessage(content=message)
        self._messages.append(system_message)
        self._save_message_to_db('system', message)
    
    def _save_message_to_db(self, sender: str, message: str, emotion_data: Optional[Dict] = None) -> None:
        """Save message to PostgreSQL database"""
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages (session_id, message, sender, emotion, severity, confidence, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                self.session_id,
                message,
                sender,
                emotion_data.get('emotion') if emotion_data else None,
                emotion_data.get('severity') if emotion_data else None,
                emotion_data.get('confidence', 0.0) if emotion_data else None
            ))
            
            # Update session activity
            cursor.execute("""
                UPDATE chat_sessions 
                SET last_activity = CURRENT_TIMESTAMP, 
                    updated_at = CURRENT_TIMESTAMP,
                    current_emotion = %s,
                    severity_level = %s
                WHERE session_id = %s
            """, (
                emotion_data.get('emotion') if emotion_data else None,
                emotion_data.get('severity') if emotion_data else None,
                self.session_id
            ))
            
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error saving message to database: {e}")
        finally:
            conn.close()
    
    def clear(self) -> None:
        """Clear all messages from memory and database"""
        self._messages = []
        
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM chat_messages WHERE session_id = %s
            """, (self.session_id,))
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error clearing messages: {e}")
        finally:
            conn.close()
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Get all messages from memory"""
        return self._messages
    
    @messages.setter
    def messages(self, value: List[BaseMessage]) -> None:
        """Set messages in memory"""
        self._messages = value


class PostgresConversationMemory(ConversationBufferMemory):
    """
    LangChain ConversationBufferMemory with PostgreSQL persistence
    Extends the standard ConversationBufferMemory with database integration
    """
    
    def __init__(self, session_id: str, user_id: str, max_messages: int = 10, **kwargs):
        """
        Initialize PostgreSQL-based conversation memory
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier from authentication
            max_messages: Maximum number of messages to keep in memory
            **kwargs: Additional arguments for ConversationBufferMemory
        """
        postgres_history = PostgresChatMessageHistory(session_id, user_id, max_messages)
        
        # Initialize parent with the PostgreSQL history
        super().__init__(
            chat_memory=postgres_history,
            return_messages=True,
            **kwargs
        )
        
        # Store session info for easy access (use object.__setattr__ to bypass validation)
        object.__setattr__(self, '_session_id', session_id)
        object.__setattr__(self, '_user_id', user_id)
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context with emotion data if available"""
        # Extract emotion data from outputs if present
        emotion_data = None
        if 'emotion' in outputs:
            emotion_data = {
                'emotion': outputs.get('emotion'),
                'severity': outputs.get('severity'),
                'confidence': outputs.get('confidence', 0.0)
            }
        
        # Save user message with emotion data
        if 'user_message' in inputs:
            self.chat_memory.add_user_message(inputs['user_message'], emotion_data)
        
        # Save AI response
        if 'response' in outputs:
            self.chat_memory.add_ai_message(outputs['response'])
        
        # Call parent method for standard LangChain integration with simplified outputs
        # LangChain expects a single output key, so we only pass the main response
        simplified_outputs = {'response': outputs.get('response', '')}
        super().save_context(inputs, simplified_outputs)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information from database"""
        conn = self.chat_memory._get_connection()
        if not conn:
            return {}
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT created_at, updated_at, last_activity, current_emotion, severity_level, is_active
                FROM chat_sessions
                WHERE session_id = %s
            """, (getattr(self, '_session_id', 'unknown'),))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'session_id': getattr(self, '_session_id', 'unknown'),
                    'user_id': getattr(self, '_user_id', 'unknown'),
                    'created_at': result['created_at'].isoformat() if result['created_at'] else None,
                    'updated_at': result['updated_at'].isoformat() if result['updated_at'] else None,
                    'last_activity': result['last_activity'].isoformat() if result['last_activity'] else None,
                    'current_emotion': result['current_emotion'],
                    'severity_level': result['severity_level'],
                    'is_active': result['is_active'],
                    'message_count': len(self.chat_memory._messages)
                }
            return {}
        except Exception as e:
            print(f"Error getting session info: {e}")
            return {}
        finally:
            conn.close()


# Utility functions for session management
def get_or_create_session(user_id: str, session_id: Optional[str] = None) -> str:
    """Get existing session or create new one"""
    if session_id:
        # Verify session exists and belongs to user
        conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id FROM chat_sessions 
                WHERE session_id = %s AND user_id = %s AND is_active = TRUE
            """, (session_id, user_id))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return session_id
        except Exception as e:
            print(f"Error checking session: {e}")
        finally:
            conn.close()
    
    # Create new session
    new_session_id = f"session-{user_id}-{int(datetime.now().timestamp())}"
    return new_session_id


def cleanup_expired_sessions(timeout_minutes: int = 30) -> None:
    """Clean up expired sessions"""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chat_sessions 
            SET is_active = FALSE 
            WHERE last_activity < NOW() - INTERVAL '%s minutes'
            AND is_active = TRUE
        """, (timeout_minutes,))
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error cleaning up sessions: {e}")
    finally:
        conn.close()
