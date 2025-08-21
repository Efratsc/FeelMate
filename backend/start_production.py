#!/usr/bin/env python3
"""
Production startup script for FeelMate Emotion-Aware Chatbot
Handles environment setup and server startup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'transformers', 
        'torch', 'langchain', 'langchain_community'
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
    """Create necessary directories for production"""
    dirs = ['logs', 'data']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")

def check_port_availability(port=8001):
    """Check if the required port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print(f"✅ Port {port} is available")
            return True
    except OSError:
        print(f"❌ Port {port} is already in use")
        print(f"Please stop any service using port {port} or change the port in server.py")
        return False

def start_server():
    """Start the production server"""
    print("\n🚀 Starting FeelMate Production Emotion-Aware Chatbot...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📚 API documentation: http://localhost:8001/docs")
    print("🏥 Health check: http://localhost:8001/health")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the server
        subprocess.run([sys.executable, "server.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main production startup function"""
    print("🏭 FeelMate Emotion-Aware Chatbot - Production Startup")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check port availability
    if not check_port_availability():
        sys.exit(1)
    
    # Start server
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()
