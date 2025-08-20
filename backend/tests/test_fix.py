#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify crisis state reset fix
"""

from chat_server import ContextAwareEmotionClassifier, ContextAwareResponseGenerator

def test_crisis_reset():
    """Test that crisis state is properly reset"""
    print("🔧 Testing Crisis State Reset Fix")
    print("=" * 40)
    
    classifier = ContextAwareEmotionClassifier()
    response_gen = ContextAwareResponseGenerator()
    
    # Test your exact conversation
    messages = [
        "i feel low",
        "i wanna kill my self", 
        "now i fell happy"
    ]
    
    conversation_history = []
    
    for i, message in enumerate(messages):
        print(f"\n📝 Message {i+1}: '{message}'")
        print("-" * 30)
        
        # Classify emotion
        emotion_data = classifier.classify_emotion_with_context(message, conversation_history)
        response = response_gen.generate_response(emotion_data, conversation_history, message)
        
        print(f"Emotion: {emotion_data['emotion']}")
        print(f"Severity: {emotion_data['severity']}")
        print(f"Confidence: {emotion_data['confidence']:.2f}")
        print(f"Needs Help: {emotion_data['needs_help']}")
        print(f"Response: {response}")
        
        # Add to conversation history
        conversation_history.append(f"user: {message}")
        conversation_history.append(f"ai: {response}")

if __name__ == "__main__":
    test_crisis_reset()
