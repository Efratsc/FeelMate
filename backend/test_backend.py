#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import fastapi
        import uvicorn
        import pydantic
        print("✓ Basic packages imported")
        
        # Test our modules
        from app.services.emotion_classifier import EmotionClassifier
        print("✓ Emotion classifier imported")
        
        # Test the classifier
        classifier = EmotionClassifier()
        result = classifier.classify_emotion("I am feeling happy today!")
        print(f"✓ Emotion classification test: {result}")
        
        print("\n🎉 All tests passed! Backend is ready to run.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()

