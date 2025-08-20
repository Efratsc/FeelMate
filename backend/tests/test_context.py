#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for context-aware emotion classification
"""

from chat_server import ContextAwareEmotionClassifier, ContextAwareResponseGenerator

def test_context_awareness():
    """Test the context-aware emotion classification"""
    print("🧠 Testing Context-Aware Emotion Classification")
    print("=" * 50)
    
    classifier = ContextAwareEmotionClassifier()
    response_gen = ContextAwareResponseGenerator()
    
    # Test 1: Normal conversation progression
    print("\n📝 Test 1: Normal to Crisis Progression")
    print("-" * 30)
    
    conversation = [
        "user: I feel normal today",
        "ai: That's good to hear! How are you doing?",
        "user: I'm feeling a bit down",
        "ai: I'm sorry to hear that. What's on your mind?",
        "user: I wanna kill myself"
    ]
    
    for i, message in enumerate(conversation):
        if message.startswith("user: "):
            user_msg = message.replace("user: ", "")
            history = conversation[:i]
            emotion_data = classifier.classify_emotion_with_context(user_msg, history)
            response = response_gen.generate_response(emotion_data, history, user_msg)
            
            print(f"Message: {user_msg}")
            print(f"Emotion: {emotion_data['emotion']} (Severity: {emotion_data['severity']})")
            print(f"Response: {response}")
            print()
    
    # Test 2: Escalating sadness
    print("\n📝 Test 2: Escalating Sadness")
    print("-" * 30)
    
    conversation = [
        "user: I'm feeling sad",
        "ai: I'm sorry to hear that. What's making you feel this way?",
        "user: Everything is hopeless",
        "ai: That sounds really difficult. Can you tell me more?",
        "user: I feel worthless and alone"
    ]
    
    for i, message in enumerate(conversation):
        if message.startswith("user: "):
            user_msg = message.replace("user: ", "")
            history = conversation[:i]
            emotion_data = classifier.classify_emotion_with_context(user_msg, history)
            response = response_gen.generate_response(emotion_data, history, user_msg)
            
            print(f"Message: {user_msg}")
            print(f"Emotion: {emotion_data['emotion']} (Severity: {emotion_data['severity']})")
            print(f"Response: {response}")
            print()
    
    # Test 3: Your specific example
    print("\n📝 Test 3: Your Example - Normal to Crisis")
    print("-" * 30)
    
    conversation = [
        "user: I feel normal",
        "ai: That's good! How are you doing today?",
        "user: I wanna kill myself"
    ]
    
    for i, message in enumerate(conversation):
        if message.startswith("user: "):
            user_msg = message.replace("user: ", "")
            history = conversation[:i]
            emotion_data = classifier.classify_emotion_with_context(user_msg, history)
            response = response_gen.generate_response(emotion_data, history, user_msg)
            
            print(f"Message: {user_msg}")
            print(f"Emotion: {emotion_data['emotion']} (Severity: {emotion_data['severity']})")
            print(f"Confidence: {emotion_data['confidence']:.2f}")
            print(f"Needs Help: {emotion_data['needs_help']}")
            print(f"Response: {response}")
            print()

if __name__ == "__main__":
    test_context_awareness()
