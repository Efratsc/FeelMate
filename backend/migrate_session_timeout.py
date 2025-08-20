#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration script to add session timeout functionality to existing database
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Minimal DB connector for migration scripts (avoids importing FastAPI app)."""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("DATABASE_URL not found in environment variables")
            return None
        return psycopg2.connect(database_url)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def migrate_session_timeout():
    """Add session timeout columns to existing tables"""
    print("🔄 Migrating database for session timeout functionality")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed")
        return
    
    try:
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chat_sessions' 
            AND column_name IN ('last_activity', 'is_active')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Existing columns: {existing_columns}")
        
        # Add last_activity column if it doesn't exist
        if 'last_activity' not in existing_columns:
            print("➕ Adding last_activity column...")
            cursor.execute("""
                ALTER TABLE chat_sessions 
                ADD COLUMN last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            print("✅ last_activity column added")
        else:
            print("✅ last_activity column already exists")
        
        # Add is_active column if it doesn't exist
        if 'is_active' not in existing_columns:
            print("➕ Adding is_active column...")
            cursor.execute("""
                ALTER TABLE chat_sessions 
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE
            """)
            print("✅ is_active column added")
        else:
            print("✅ is_active column already exists")
        
        # Update existing sessions to have proper timestamps
        print("🔄 Updating existing sessions...")
        cursor.execute("""
            UPDATE chat_sessions 
            SET last_activity = updated_at, is_active = TRUE 
            WHERE last_activity IS NULL OR is_active IS NULL
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        print("📋 Session timeout features are now available:")
        print("• Sessions will expire after 30 minutes of inactivity")
        print("• Automatic cleanup of old sessions and messages")
        print("• Session activity tracking")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_session_timeout()
