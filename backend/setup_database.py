#!/usr/bin/env python3
"""
Database Setup Script for FeelMate
Creates all necessary tables for better-auth and chat functionality
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def create_database_tables():
    """Create all necessary database tables"""
    
    # Get database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        print("🔗 Connected to database successfully")
        
        # Create better-auth tables
        print("📋 Creating better-auth tables...")
        
        # Users table (better-auth)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Sessions table (better-auth)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Verification tokens table (better-auth)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_tokens (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Chat sessions table
        print("💬 Creating chat tables...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_emotion TEXT,
                severity_level TEXT,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        
        # Chat messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
                message TEXT NOT NULL,
                sender TEXT NOT NULL,
                emotion TEXT,
                severity TEXT,
                confidence FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes for better performance
        print("⚡ Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database tables created successfully!")
        print("\n📊 Tables created:")
        print("  • users (better-auth)")
        print("  • sessions (better-auth)")
        print("  • verification_tokens (better-auth)")
        print("  • chat_sessions")
        print("  • chat_messages")
        print("\n🔍 Indexes created for optimal performance")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def create_test_user():
    """Create a test user for development"""
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Check if test user already exists
        cursor.execute('SELECT id FROM "user" WHERE email = %s', ("test@feelmate.com",))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("ℹ️ Test user already exists")
            cursor.close()
            conn.close()
            return True
        
        # Create test user (password: test123)
        import hashlib
        import secrets
        
        user_id = secrets.token_urlsafe(32)
        email = "test@feelmate.com"
        password = "test123"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO "user" (id, email, "hashedPassword", name, "emailVerified", "createdAt", "updatedAt")
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (user_id, email, hashed_password, "Test User", False))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Test user created successfully!")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print("⚠️  Note: This is a development user only!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up FeelMate Database...")
    print("=" * 50)
    
    # Create tables
    if create_database_tables():
        print("\n" + "=" * 50)
        print("🎯 Database setup completed successfully!")
        
        # Ask if user wants to create test user
        response = input("\n🤔 Create a test user for development? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            create_test_user()
        
        print("\n✨ You can now start the application!")
        print("📝 Next steps:")
        print("  1. Start the backend: cd backend && python server.py")
        print("  2. Start the frontend: cd frontend && npm run dev")
        print("  3. Sign in with the test user (if created)")
        
    else:
        print("\n❌ Database setup failed!")
        print("📝 Please check your DATABASE_URL and try again.")

