#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secure setup script for FeelMate Backend
"""

import os
import shutil

def secure_setup():
    """Secure environment setup without exposing credentials"""
    print("🔒 FeelMate Backend Secure Setup")
    print("=" * 40)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        
        env_content = """# Database Configuration - Same as frontend
# Copy your DATABASE_URL from your frontend .env file
DATABASE_URL=your_database_url_here

# Server Configuration
PORT=8001
HOST=0.0.0.0
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created")
        print("\n📋 NEXT STEPS:")
        print("1. Open the .env file in your editor")
        print("2. Replace 'your_database_url_here' with your actual DATABASE_URL")
        print("3. Copy the DATABASE_URL from your frontend .env file")
        print("4. Save the file")
        print("5. Run: python setup_database.py")
    else:
        print("✅ .env file already exists")
        print("📝 If you need to update it, edit the .env file manually")

if __name__ == "__main__":
    secure_setup()
