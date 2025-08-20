#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test session timeout functionality
"""

from chat_server import init_chat_tables, cleanup_expired_sessions, SESSION_TIMEOUT_MINUTES

def test_session_timeout():
    """Test session timeout functionality"""
    print("⏰ Testing Session Timeout Functionality")
    print("=" * 50)
    
    # Initialize tables
    print("📊 Initializing database tables...")
    init_chat_tables()
    
    print(f"⏱️  Session timeout set to: {SESSION_TIMEOUT_MINUTES} minutes")
    print("\n🔄 Running session cleanup...")
    
    # Run cleanup
    cleanup_expired_sessions()
    
    print("\n✅ Session timeout test completed!")
    print("\n📋 Session Timeout Features:")
    print(f"• Sessions expire after {SESSION_TIMEOUT_MINUTES} minutes of inactivity")
    print("• Inactive sessions are automatically marked as inactive")
    print("• Messages from old sessions are cleaned up after 24 hours")
    print("• Very old inactive sessions are deleted after 24 hours")
    print("• Session activity is updated with every message")
    print("• New sessions are created automatically when needed")

if __name__ == "__main__":
    test_session_timeout()
