"""
Simple test to verify PostgresConversationMemory fix
"""

import os
from dotenv import load_dotenv
from postgres_memory import PostgresConversationMemory, get_or_create_session

load_dotenv()

def test_memory_creation():
    """Test that PostgresConversationMemory can be created without errors"""
    try:
        print("Testing PostgresConversationMemory creation...")
        
        # Create memory instance
        memory = PostgresConversationMemory(
            session_id="test-session-123",
            user_id="test-user-123",
            max_messages=10
        )
        
        print("✅ PostgresConversationMemory created successfully")
        print(f"Session ID: {getattr(memory, '_session_id', 'Not set')}")
        print(f"User ID: {getattr(memory, '_user_id', 'Not set')}")
        print(f"Chat memory type: {type(memory.chat_memory)}")
        
        # Test adding messages
        memory.chat_memory.add_user_message("Hello, I'm feeling sad")
        memory.chat_memory.add_ai_message("I'm here to listen. Can you tell me more?")
        
        print(f"✅ Messages added successfully. Count: {len(memory.chat_memory._messages)}")
        
        # Test session info
        session_info = memory.get_session_info()
        print(f"✅ Session info retrieved: {session_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing PostgresConversationMemory fix...")
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ Error: DATABASE_URL environment variable not set")
        print("Please set your PostgreSQL connection string in .env file")
        exit(1)
    
    success = test_memory_creation()
    
    if success:
        print("\n✅ All tests passed! The fix is working correctly.")
    else:
        print("\n❌ Tests failed. There may still be an issue.")
