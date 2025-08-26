# PostgreSQL LangChain Memory Integration for FeelMate

## Overview

This implementation provides a complete, production-ready solution for persistent, per-user chat memory using LangChain with PostgreSQL. It replaces the previous manual database operations with a seamless LangChain integration that maintains conversation context across sessions.

## Architecture

### Core Components

1. **`PostgresChatMessageHistory`** - Custom LangChain ChatMessageHistory implementation
2. **`PostgresConversationMemory`** - Extended ConversationBufferMemory with PostgreSQL persistence
3. **Enhanced Chatbot** - Updated EmotionAwareChatbot with LangChain memory integration
4. **API Endpoints** - New endpoints for session management and history retrieval

### Database Schema

The implementation uses your existing PostgreSQL schema:

```sql
-- Chat sessions table
CREATE TABLE chat_sessions (
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
);

-- Chat messages table
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    message TEXT NOT NULL,
    sender TEXT NOT NULL,
    emotion TEXT,
    severity TEXT,
    confidence FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);
```

## Key Features

### 1. Persistent Memory
- **Automatic Loading**: Conversation history is automatically loaded when a session is initialized
- **Real-time Persistence**: Messages are saved to PostgreSQL immediately
- **Session Continuity**: Conversations continue seamlessly across server restarts

### 2. LangChain Integration
- **Standard Interface**: Uses LangChain's standard memory interfaces
- **Message Types**: Supports HumanMessage, AIMessage, and SystemMessage
- **Context Management**: Integrates with LangChain's conversation chains

### 3. Enhanced Context
- **Session Context**: Provides session metadata for better response generation
- **Emotion Tracking**: Stores emotion data with each message
- **Crisis Detection**: Maintains crisis detection state across conversations

### 4. Session Management
- **Automatic Session Creation**: Sessions are created automatically when needed
- **Session Validation**: Ensures sessions belong to the correct user
- **Activity Tracking**: Monitors session activity and handles timeouts

## Usage Examples

### Basic Chat with Memory

```python
from chatbot import get_chatbot

chatbot = get_chatbot()

# First message - creates new session
response1 = chatbot.chat(
    user_message="I'm feeling really sad today",
    user_id="user_123"
)

# Continue conversation - uses same session
response2 = chatbot.chat(
    user_message="I lost my job and I don't know what to do",
    user_id="user_123",
    session_id=response1.session_id
)
```

### Direct Memory Usage

```python
from postgres_memory import PostgresConversationMemory

# Create memory instance
memory = PostgresConversationMemory(
    session_id="session-123",
    user_id="user_123",
    max_messages=10
)

# Add messages
memory.chat_memory.add_user_message("Hello, I'm feeling overwhelmed")
memory.chat_memory.add_ai_message("I'm here to listen. Can you tell me more?")

# Get session info
session_info = memory.get_session_info()
print(f"Session: {session_info}")
```

### Session Management

```python
from postgres_memory import get_or_create_session, cleanup_expired_sessions

# Get or create session
session_id = get_or_create_session("user_123", existing_session_id)

# Clean up expired sessions
cleanup_expired_sessions(timeout_minutes=30)
```

## API Endpoints

### Chat Endpoint
```http
POST /api/chat/send-message
Content-Type: application/json

{
    "message": "I'm feeling sad today",
    "user_id": "user_123",
    "session_id": "session-456"  // Optional
}
```

### Session Information
```http
GET /api/chat/session/{session_id}?user_id={user_id}
```

### Conversation History
```http
GET /api/chat/history/{session_id}?user_id={user_id}
```

### Session Cleanup
```http
POST /api/chat/cleanup-sessions
```

## Implementation Details

### 1. PostgresChatMessageHistory Class

This class implements LangChain's `ChatMessageHistory` interface:

```python
class PostgresChatMessageHistory:
    def __init__(self, session_id: str, user_id: str, max_messages: int = 10):
        # Initialize with session and user info
        # Automatically loads existing messages
        # Ensures session exists in database
    
    def add_user_message(self, message: str, emotion_data: Optional[Dict] = None):
        # Adds user message to memory and database
    
    def add_ai_message(self, message: str, emotion_data: Optional[Dict] = None):
        # Adds AI message to memory and database
    
    def clear(self):
        # Clears all messages from memory and database
```

### 2. PostgresConversationMemory Class

Extends LangChain's `ConversationBufferMemory`:

```python
class PostgresConversationMemory(ConversationBufferMemory):
    def __init__(self, session_id: str, user_id: str, max_messages: int = 10):
        # Initializes with PostgreSQL history
        # Provides standard LangChain memory interface
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]):
        # Saves context with emotion data
        # Updates session activity
    
    def get_session_info(self) -> Dict[str, Any]:
        # Returns detailed session information
```

### 3. Enhanced Chatbot Integration

The chatbot now uses LangChain memory seamlessly:

```python
def chat(self, user_message, user_id, session_id=None):
    # Get or create session
    session_id = get_or_create_session(user_id, session_id)
    
    # Initialize PostgreSQL-based LangChain memory
    memory = PostgresConversationMemory(
        session_id=session_id,
        user_id=user_id,
        max_messages=10
    )
    
    # Get conversation history from LangChain memory
    history_messages = memory.chat_memory.messages
    
    # Generate response with context
    # Save context via LangChain memory
    memory.save_context(inputs, outputs)
```

## Configuration

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://username:password@localhost:5432/feelmate_db

# Optional
LOG_LEVEL=info
MAX_MEMORY_MESSAGES=10
SESSION_TIMEOUT_MINUTES=30
```

### Database Connection

The implementation uses your existing PostgreSQL connection pattern:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

connection = psycopg2.connect(
    os.getenv("DATABASE_URL"), 
    cursor_factory=RealDictCursor
)
```

## Best Practices

### 1. Session Management
- Always pass `user_id` for proper session isolation
- Use `session_id` to continue conversations
- Implement session cleanup for expired sessions

### 2. Memory Optimization
- Set appropriate `max_messages` to control memory usage
- Use session timeouts to prevent memory bloat
- Monitor database performance with large conversation histories

### 3. Error Handling
- Handle database connection failures gracefully
- Implement fallback mechanisms for memory operations
- Log errors for debugging and monitoring

### 4. Security
- Validate user ownership of sessions
- Sanitize user inputs before database storage
- Implement proper access controls

## Migration from Previous Implementation

### Before (Manual Database Operations)
```python
# Manual database operations
self._save_message(session_id, "user", user_message)
self._save_message(session_id, "ai", ai_response)
last_messages = self._get_last_messages(session_id)
```

### After (LangChain Integration)
```python
# Seamless LangChain integration
memory = PostgresConversationMemory(session_id, user_id)
memory.save_context(inputs, outputs)
history_messages = memory.chat_memory.messages
```

## Testing

Run the example usage to test the integration:

```bash
cd backend
python example_usage.py
```

This will demonstrate:
- Basic chat functionality
- Session management
- Memory persistence
- Crisis detection
- History retrieval

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` is set correctly
   - Check PostgreSQL server is running
   - Ensure database tables exist

2. **Session Not Found**
   - Verify session belongs to the correct user
   - Check session hasn't expired
   - Ensure session_id format is correct

3. **Memory Not Persisting**
   - Check database permissions
   - Verify transaction commits
   - Monitor for database errors

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

### Database Optimization
- Index on `session_id` and `user_id` columns
- Regular cleanup of expired sessions
- Monitor query performance with large datasets

### Memory Management
- Limit `max_messages` based on your use case
- Implement message archiving for long conversations
- Consider pagination for history retrieval

### Scaling
- Use connection pooling for high concurrency
- Implement caching for frequently accessed sessions
- Consider read replicas for history queries

## Future Enhancements

### Potential Improvements
1. **Message Archiving**: Archive old messages to separate tables
2. **Analytics Integration**: Add conversation analytics and insights
3. **Multi-modal Support**: Support for images, audio, and other media
4. **Advanced Caching**: Redis-based caching for improved performance
5. **Real-time Updates**: WebSocket support for real-time conversation updates

### Integration Opportunities
1. **User Analytics**: Track conversation patterns and user engagement
2. **Content Moderation**: Integrate with content moderation services
3. **Multi-language Support**: Extend to support multiple languages
4. **Voice Integration**: Add voice-to-text and text-to-speech capabilities

## Conclusion

This PostgreSQL LangChain integration provides a robust, scalable solution for persistent conversation memory. It maintains the simplicity of LangChain's standard interfaces while providing the reliability and performance of PostgreSQL storage.

The implementation is production-ready and includes comprehensive error handling, session management, and performance optimizations. It seamlessly integrates with your existing FeelMate architecture while providing enhanced functionality for conversation memory and context management.
