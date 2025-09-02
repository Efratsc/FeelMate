#!/usr/bin/env python3
"""
Simple setup script to create .env file for FeelMate backend
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with default values"""
    env_content = """# FeelMate Backend Environment Configuration

# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=false
LOG_LEVEL=info

# Database Configuration (PostgreSQL)
# Replace with your actual database URL
DATABASE_URL=postgresql://username:password@localhost:5432/feelmate_db

# Model Configuration
EMOTION_MODEL=j-hartmann/emotion-english-distilroberta-base
DEVICE=cpu

# Memory Configuration
MEMORY_FILE=data/conversation_memory.json
MAX_MEMORY_MESSAGES=5

# LangGraph Configuration
USE_LANGRAPH=true
"""
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing .env file")
            return
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("📝 Please edit .env file and set your DATABASE_URL")
    print("   Example: DATABASE_URL=postgresql://user:pass@host:port/dbname")

def main():
    print("🔧 FeelMate Backend Environment Setup")
    print("=" * 40)
    
    create_env_file()
    
    print("\n📋 Next steps:")
    print("1. Edit .env file and set your DATABASE_URL")
    print("2. Run: python start_langgraph.py")

if __name__ == "__main__":
    main()
