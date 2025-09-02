#!/usr/bin/env python3
"""
Startup script for FeelMate LLM-free LangGraph server
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Set up environment variables"""
    # You can set your DATABASE_URL here or it will use the one from .env
    # For now, let's use a placeholder that you can replace
    if not os.getenv("DATABASE_URL"):
        print("⚠️  DATABASE_URL not set. Please set it in your environment or .env file")
        print("Example: DATABASE_URL=postgresql://username:password@localhost:5432/feelmate_db")
        
        # You can uncomment and modify this line to set it directly:
        # os.environ["DATABASE_URL"] = "postgresql://username:password@localhost:5432/feelmate_db"
        
        return False
    
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'transformers', 
        'torch', 'psycopg2', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ['logs', 'data']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")

def start_server():
    """Start the LangGraph server"""
    print("\n🚀 Starting FeelMate LLM-free LangGraph Server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📚 API documentation: http://localhost:8001/docs")
    print("🏥 Health check: http://localhost:8001/health")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the server
        subprocess.run([sys.executable, "server_langgraph.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🧠 FeelMate LLM-free LangGraph Server - Startup")
    print("=" * 60)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed")
        print("Please set DATABASE_URL and try again")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Start server
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()
