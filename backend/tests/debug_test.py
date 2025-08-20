#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug test for emotion classification
"""

from chat_server import ContextAwareEmotionClassifier

def debug_emotion_classification():
    """Debug the emotion classification for specific messages"""
    print("🔍 Debugging Emotion Classification")
    print("=" * 40)
    
    classifier = ContextAwareEmotionClassifier()
    
    # Test your exact messages
    messages = [
        "i fell sad",
        "i am normal now", 
        "i wanna kill my self"
    ]
    
    conversation_history = []
    
    for i, message in enumerate(messages):
        print(f"\n📝 Message {i+1}: '{message}'")
        print("-" * 30)
        
        # Classify emotion
        emotion_data = classifier.classify_emotion_with_context(message, conversation_history)
        
        print(f"Emotion: {emotion_data['emotion']}")
        print(f"Severity: {emotion_data['severity']}")
        print(f"Confidence: {emotion_data['confidence']:.2f}")
        print(f"Needs Help: {emotion_data['needs_help']}")
        
        # Add to conversation history
        conversation_history.append(f"user: {message}")
        
        # Simulate AI response
        conversation_history.append("ai: Thank you for sharing.")

if __name__ == "__main__":
    debug_emotion_classification()
