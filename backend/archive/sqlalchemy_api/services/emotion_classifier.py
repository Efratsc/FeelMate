#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import joblib
import os
import numpy as np
from typing import Dict, List

class EmotionClassifier:
    def __init__(self):
        self.model_path = "app/ml/models/emotion_classifier.pkl"
        self.vectorizer_path = "app/ml/models/vectorizer.pkl"
        self.model = None
        self.vectorizer = None
        self.load_model()
    
    def load_model(self):
        """Load trained model and vectorizer"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                print("Trained ML model loaded successfully")
            else:
                print("Trained model not found, using fallback keyword classification")
                self.model = None
                self.vectorizer = None
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Using fallback keyword classification")
            self.model = None
            self.vectorizer = None
    
    def classify_emotion(self, text: str) -> Dict:
        """Classify emotion using trained model or fallback to keywords"""
        if self.model is not None and self.vectorizer is not None:
            return self._ml_classification(text)
        else:
            return self._fallback_classification(text)
    
    def _ml_classification(self, text: str) -> Dict:
        """Classify emotion using trained ML model"""
        try:
            # Vectorize text
            X = self.vectorizer.transform([text])
            
            # Predict
            emotion = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            confidence = max(probabilities)
            
            # Map emotions to severity
            severity_map = {
                "joy": 2,
                "neutral": 4,
                "surprise": 5,
                "fear": 6,
                "anger": 7,
                "sadness": 8,
                "disgust": 6
            }
            
            severity = severity_map.get(emotion, 4)
            needs_help = severity >= 6
            
            return {
                "emotion": emotion,
                "confidence": confidence,
                "severity": severity,
                "needs_immediate_help": needs_help
            }
        except Exception as e:
            print(f"ML classification error: {e}")
            return self._fallback_classification(text)
    
    def _fallback_classification(self, text: str) -> Dict:
        """Fallback keyword-based emotion classification"""
        emotion_keywords = {
            "depression": ["sad", "depressed", "hopeless", "worthless", "empty", "tired", "exhausted"],
            "anxiety": ["anxious", "worried", "stressed", "nervous", "panic", "fear", "scared"],
            "anger": ["angry", "mad", "furious", "hate", "irritated", "frustrated"],
            "joy": ["happy", "joy", "excited", "great", "wonderful", "amazing"],
            "calm": ["peaceful", "relaxed", "serene", "calm", "content"],
            "crisis": ["suicide", "kill myself", "end it all", "no reason to live"]
        }
        
        text_lower = text.lower()
        
        # Check for crisis first
        if any(word in text_lower for word in emotion_keywords["crisis"]):
            return {
                "emotion": "crisis",
                "severity": 10,
                "confidence": 0.95,
                "needs_immediate_help": True
            }
        
        # Check other emotions
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            if emotion == "crisis":
                continue
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            severity = self._get_severity(dominant_emotion)
            confidence = min(emotion_scores[dominant_emotion] / len(emotion_keywords[dominant_emotion]), 1.0)
            
            return {
                "emotion": dominant_emotion,
                "severity": severity,
                "confidence": confidence,
                "needs_immediate_help": severity >= 8
            }
        
        return {
            "emotion": "neutral",
            "severity": 4,
            "confidence": 0.5,
            "needs_immediate_help": False
        }
    
    def _get_severity(self, emotion: str) -> int:
        severity_map = {
            "joy": 2, "calm": 3, "neutral": 4, "anxiety": 6,
            "anger": 7, "depression": 8, "crisis": 10
        }
        return severity_map.get(emotion, 4)
    
    def generate_response(self, emotion_data: Dict) -> str:
        emotion = emotion_data["emotion"]
        severity = emotion_data["severity"]
        
        responses = {
            "crisis": "I am very concerned about what you are sharing. Your life has immense value. Please call the National Suicide Prevention Lifeline at 988 immediately, or text HOME to 741741 to reach Crisis Text Line. You are not alone.",
            "depression": "I hear that you are feeling down, and your feelings are completely valid. It is okay to feel this way. Would you like to talk more about what is causing these feelings? Consider reaching out to a mental health professional - they can help.",
            "anxiety": "Anxiety can be really overwhelming. Let us take a deep breath together. What specific thoughts are running through your mind right now? Talking to a therapist might help you develop coping strategies.",
            "anger": "I understand you are feeling angry. It is important to acknowledge these feelings. What triggered this anger? Sometimes talking to someone can help process these emotions.",
            "joy": "It is wonderful that you are feeling happy! What brought on these positive feelings? I am here to celebrate with you.",
            "calm": "It sounds like you are in a peaceful state. That is wonderful. How can I support you today?",
            "neutral": "Thank you for sharing. I am here to listen and support you. How are you feeling today?",
            "sadness": "I hear that you are feeling sad, and your feelings are completely valid. It is okay to feel this way. Would you like to talk more about what is causing these feelings?",
            "fear": "Fear can be really overwhelming. Let us take a deep breath together. What specific thoughts are running through your mind right now?",
            "surprise": "It sounds like something unexpected happened. How are you processing this? I am here to listen.",
            "disgust": "I understand you are feeling disgusted. It is important to acknowledge these feelings. What triggered this reaction?"
        }
        return responses.get(emotion, "I am here to listen and support you.")
    
    def get_resources(self, emotion_data: Dict) -> List[Dict]:
        if emotion_data["needs_immediate_help"]:
            return [
                {"name": "National Suicide Prevention Lifeline", "phone": "988", "description": "24/7 crisis support"},
                {"name": "Crisis Text Line", "text": "HOME to 741741", "description": "24/7 crisis support via text"}
            ]
        return [
            {"name": "Psychology Today", "url": "https://www.psychologytoday.com/us/therapists", "description": "Find therapists and psychiatrists"},
            {"name": "BetterHelp", "url": "https://www.betterhelp.com", "description": "Online therapy platform"}
        ]
