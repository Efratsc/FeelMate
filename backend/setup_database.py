#!/usr/bin/env python3
"""
Database setup script for FeelMate backend
This script helps you configure and test the database connection
"""

import os
import psycopg2
from dotenv import load_dotenv

def create_env_file():
    """Create .env file with database configuration"""
    print("�� Creating .env file...")
    print("🔒 SECURITY: Database credentials will not be exposed in code")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return
    
    env_content = """# Database Configuration - Same as frontend
# Copy your DATABASE_URL from your frontend .env file
DATABASE_URL=your_database_url_here

# Server Configuration
PORT=8001
HOST=0.0.0.0
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default database configuration")
        print("📝 Please update the database credentials in .env file if needed")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def test_database_connection():
    """Test database connection"""
    load_dotenv()
    
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
        
        connection = psycopg2.connect(database_url)
        
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("✅ Database connection successful!")
        print(f"📊 PostgreSQL version: {version[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except psycopg2.OperationalError as e:
        print("❌ Database connection failed!")
        print(f"Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if the database 'feelmate' exists")
        print("3. Verify username and password in .env file")
        print("4. Ensure PostgreSQL is listening on the correct port")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_database():
    """Create the feelmate database if it doesn't exist"""
    try:
        # Connect using DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return
        
        connection = psycopg2.connect(database_url)
        
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Since we're using Neon, the database already exists
        print("✅ Using existing Neon database")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")

def main():
    print("🚀 FeelMate Database Setup")
    print("=" * 40)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        create_env_file()
    else:
        print("✅ .env file already exists")
    
    print("\n📊 Testing database connection...")
    
    # Try to create database first
    create_database()
    
    # Test connection
    if test_database_connection():
        print("\n🎉 Database setup completed successfully!")
        print("You can now run the chat server with: python chat_server.py")
    else:
        print("\n⚠️  Please fix the database connection issues before running the server")

if __name__ == "__main__":
    main()
