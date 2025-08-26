"""
Example usage of FeelMate PostgreSQL LangChain Memory Integration

This file demonstrates how to use the custom PostgreSQL-based LangChain memory
system with the emotion-aware chatbot.
"""

import os
from dotenv import load_dotenv
from chatbot import get_chatbot
from postgres_memory import PostgresConversationMemory, get_or_create_session

load_dotenv()

def example_basic_chat():
    """
    Basic example of using the chatbot with PostgreSQL memory
    """
    print("=== Basic Chat Example ===")
    
    # Initialize chatbot
    chatbot = get_chatbot()
    
    # Example user ID (from your authentication system)
    user_id = "user_123"
    
    # First message - creates new session
    print("\n1. First message (creates new session):")
    response1 = chatbot.chat(
        user_message="I'm feeling really sad today",
        user_id=user_id
    )
    print(f"Response: {response1.response}")
    print(f"Emotion: {response1.emotion}")
    print(f"Session ID: {response1.session_id}")
    
    # Second message - continues same session
    print("\n2. Second message (continues session):")
    response2 = chatbot.chat(
        user_message="I lost my job and I don't know what to do",
        user_id=user_id,
        session_id=response1.session_id
    )
    print(f"Response: {response2.response}")
    print(f"Emotion: {response2.emotion}")
    
    # Third message - shows memory working
    print("\n3. Third message (memory context):")
    response3 = chatbot.chat(
        user_message="I'm starting to feel a bit better",
        user_id=user_id,
        session_id=response1.session_id
    )
    print(f"Response: {response3.response}")
    print(f"Emotion: {response3.emotion}")

def example_session_management():
    """
    Example of session management and history retrieval
    """
    print("\n=== Session Management Example ===")
    
    chatbot = get_chatbot()
    user_id = "user_456"
    
    # Create a session and have a conversation
    session_id = get_or_create_session(user_id)
    
    # Send several messages
    messages = [
        "I'm feeling anxious about my upcoming presentation",
        "I keep thinking about all the things that could go wrong",
        "My heart is racing and I can't sleep"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n{i}. User: {message}")
        response = chatbot.chat(
            user_message=message,
            user_id=user_id,
            session_id=session_id
        )
        print(f"AI: {response.response}")
        print(f"Emotion: {response.emotion}")
    
    # Get session information
    print(f"\n=== Session Information ===")
    session_info = chatbot.get_session_info(session_id, user_id)
    print(f"Session ID: {session_info.get('session_id')}")
    print(f"User ID: {session_info.get('user_id')}")
    print(f"Current Emotion: {session_info.get('current_emotion')}")
    print(f"Severity Level: {session_info.get('severity_level')}")
    print(f"Message Count: {session_info.get('message_count')}")
    print(f"Last Activity: {session_info.get('last_activity')}")
    
    # Get conversation history
    print(f"\n=== Conversation History ===")
    history = chatbot.get_conversation_history(session_id, user_id)
    for msg in history:
        print(f"{msg['sender'].upper()}: {msg['message']}")

def example_direct_memory_usage():
    """
    Example of using the PostgreSQL memory directly with LangChain
    """
    print("\n=== Direct Memory Usage Example ===")
    
    user_id = "user_789"
    session_id = get_or_create_session(user_id)
    
    # Create PostgreSQL memory instance
    memory = PostgresConversationMemory(
        session_id=session_id,
        user_id=user_id,
        max_messages=10
    )
    
    # Add messages directly
    memory.chat_memory.add_user_message("Hello, I'm feeling overwhelmed")
    memory.chat_memory.add_ai_message("I'm here to listen. Can you tell me more about what's making you feel overwhelmed?")
    
    # Get messages from memory
    print("Messages in memory:")
    for msg in memory.chat_memory.messages:
        if hasattr(msg, 'content'):
            sender = "User" if hasattr(msg, 'type') and msg.type == "human" else "AI"
            print(f"{sender}: {msg.content}")
    
    # Get session info
    session_info = memory.get_session_info()
    print(f"\nSession Info: {session_info}")

def example_crisis_detection():
    """
    Example of crisis detection with memory persistence
    """
    print("\n=== Crisis Detection Example ===")
    
    chatbot = get_chatbot()
    user_id = "user_crisis"
    
    # Crisis message
    response = chatbot.chat(
        user_message="I'm thinking about ending my life",
        user_id=user_id
    )
    
    print(f"User: I'm thinking about ending my life")
    print(f"AI: {response.response}")
    print(f"Crisis Detected: {response.crisis_detected}")
    print(f"Session ID: {response.session_id}")
    
    # Follow-up message
    response2 = chatbot.chat(
        user_message="I don't know if I can go on anymore",
        user_id=user_id,
        session_id=response.session_id
    )
    
    print(f"\nUser: I don't know if I can go on anymore")
    print(f"AI: {response2.response}")
    print(f"Crisis Detected: {response2.crisis_detected}")

if __name__ == "__main__":
    print("FeelMate PostgreSQL LangChain Memory Integration Examples")
    print("=" * 60)
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ Error: DATABASE_URL environment variable not set")
        print("Please set your PostgreSQL connection string in .env file")
        exit(1)
    
    try:
        # Run examples
        example_basic_chat()
        example_session_management()
        example_direct_memory_usage()
        example_crisis_detection()
        
        print("\n✅ All examples completed successfully!")
        print("\nKey Features Demonstrated:")
        print("- Persistent conversation memory in PostgreSQL")
        print("- Session management and tracking")
        print("- Emotion detection and crisis monitoring")
        print("- LangChain integration with custom memory")
        print("- Conversation history retrieval")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Make sure your PostgreSQL database is running and accessible")
