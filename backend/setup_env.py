#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secure environment setup script for FeelMate Backend
"""

import os
import shutil

def setup_environment():
    """Set up environment file securely"""
    print("🔒 FeelMate Backend Environment Setup")
    print("=" * 40)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        print("⚠️  If you need to update it, manually edit the .env file")
        return
    
    # Copy from template
    if os.path.exists('env.template'):
        shutil.copy('env.template', '.env')
        print("✅ Created .env file from template")
        print("\n📝 NEXT STEPS:")
        print("1. Edit .env file and replace 'your_database_url_here' with your actual DATABASE_URL")
        print("2. Copy the DATABASE_URL from your frontend .env file")
        print("3. Run: python setup_database.py")
    else:
        print("❌ env.template not found")
        print("Creating basic .env file...")
        
        env_content = """# Database Configuration - Same as frontend
# Replace with your actual DATABASE_URL from your frontend .env file
DATABASE_URL=your_database_url_here

# Server Configuration
PORT=8001
HOST=0.0.0.0
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file")
        print("\n📝 NEXT STEPS:")
        print("1. Edit .env file and replace 'your_database_url_here' with your actual DATABASE_URL")
        print("2. Copy the DATABASE_URL from your frontend .env file")
        print("3. Run: python setup_database.py")

if __name__ == "__main__":
    setup_environment()
