#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from typing import List, Dict
import json

class EmotionDataset:
    def __init__(self):
        self.emotions = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"]
        self.data = []
    
    def create_synthetic_dataset(self):
        """Create synthetic emotion dataset for training"""
        synthetic_data = [
            # Joy
            {"text": "I am so happy today!", "emotion": "joy"},
            {"text": "This is amazing news!", "emotion": "joy"},
            {"text": "I feel wonderful and excited", "emotion": "joy"},
            {"text": "Today was the best day ever", "emotion": "joy"},
            {"text": "I am thrilled about this", "emotion": "joy"},
            {"text": "Everything is going great", "emotion": "joy"},
            {"text": "I feel so blessed and grateful", "emotion": "joy"},
            {"text": "This makes me so happy", "emotion": "joy"},
            
            # Sadness
            {"text": "I feel so sad and hopeless", "emotion": "sadness"},
            {"text": "Everything is going wrong", "emotion": "sadness"},
            {"text": "I am feeling depressed", "emotion": "sadness"},
            {"text": "Life is so difficult right now", "emotion": "sadness"},
            {"text": "I feel empty inside", "emotion": "sadness"},
            {"text": "Nothing makes me happy anymore", "emotion": "sadness"},
            {"text": "I am so tired of everything", "emotion": "sadness"},
            {"text": "I feel worthless and alone", "emotion": "sadness"},
            
            # Anger
            {"text": "I am so angry right now", "emotion": "anger"},
            {"text": "This makes me furious", "emotion": "anger"},
            {"text": "I hate this situation", "emotion": "anger"},
            {"text": "I am really irritated", "emotion": "anger"},
            {"text": "This is so frustrating", "emotion": "anger"},
            {"text": "I am mad about this", "emotion": "anger"},
            {"text": "I cannot stand this anymore", "emotion": "anger"},
            {"text": "This is ridiculous", "emotion": "anger"},
            
            # Fear
            {"text": "I am scared about what might happen", "emotion": "fear"},
            {"text": "I am afraid of the future", "emotion": "fear"},
            {"text": "This is terrifying", "emotion": "fear"},
            {"text": "I am worried about everything", "emotion": "fear"},
            {"text": "I feel anxious and nervous", "emotion": "fear"},
            {"text": "I am panicking right now", "emotion": "fear"},
            {"text": "I am so afraid", "emotion": "fear"},
            {"text": "This scares me", "emotion": "fear"},
            
            # Surprise
            {"text": "I cannot believe this happened", "emotion": "surprise"},
            {"text": "This is so unexpected", "emotion": "surprise"},
            {"text": "I am shocked by this news", "emotion": "surprise"},
            {"text": "Wow, this is amazing", "emotion": "surprise"},
            {"text": "I never saw this coming", "emotion": "surprise"},
            {"text": "This is unbelievable", "emotion": "surprise"},
            {"text": "I am so surprised", "emotion": "surprise"},
            {"text": "This caught me off guard", "emotion": "surprise"},
            
            # Disgust
            {"text": "This is disgusting", "emotion": "disgust"},
            {"text": "I am repulsed by this", "emotion": "disgust"},
            {"text": "This is so gross", "emotion": "disgust"},
            {"text": "I cannot stand this", "emotion": "disgust"},
            {"text": "This is revolting", "emotion": "disgust"},
            {"text": "I am sickened by this", "emotion": "disgust"},
            {"text": "This is awful", "emotion": "disgust"},
            {"text": "I hate this", "emotion": "disgust"},
            
            # Neutral
            {"text": "I am feeling okay today", "emotion": "neutral"},
            {"text": "Nothing special happened", "emotion": "neutral"},
            {"text": "I am just going through the day", "emotion": "neutral"},
            {"text": "Everything is normal", "emotion": "neutral"},
            {"text": "I feel fine", "emotion": "neutral"},
            {"text": "Today is just another day", "emotion": "neutral"},
            {"text": "I am doing alright", "emotion": "neutral"},
            {"text": "Nothing to report", "emotion": "neutral"},
        ]
        
        # Add more variations
        for item in synthetic_data:
            self.data.append(item)
            # Add variations
            variations = [
                item["text"].lower(),
                item["text"].upper(),
                item["text"] + ".",
                "I think " + item["text"],
                "Today " + item["text"],
                item["text"] + " and I do not know what to do",
                "I feel like " + item["text"],
                "It seems like " + item["text"]
            ]
            for variation in variations:
                self.data.append({"text": variation, "emotion": item["emotion"]})
        
        return self.data
    
    def save_dataset(self, filename: str = "emotion_dataset.json"):
        """Save dataset to file"""
        os.makedirs("app/ml/data", exist_ok=True)
        with open(f"app/ml/data/{filename}", "w", encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
    
    def load_dataset(self, filename: str = "emotion_dataset.json"):
        """Load dataset from file"""
        with open(f"app/ml/data/{filename}", "r", encoding='utf-8') as f:
            self.data = json.load(f)
        return self.data

class EmotionModelTrainer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model_path = "app/ml/models/emotion_classifier.pkl"
        self.vectorizer_path = "app/ml/models/vectorizer.pkl"
    
    def prepare_data(self, data: List[Dict]):
        """Prepare data for training"""
        texts = [item["text"] for item in data]
        emotions = [item["emotion"] for item in data]
        
        # Vectorize text
        X = self.vectorizer.fit_transform(texts)
        y = emotions
        
        return X, y
    
    def train_model(self, X, y):
        """Train the emotion classification model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
    
    def save_model(self):
        """Save trained model and vectorizer"""
        os.makedirs("app/ml/models", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        print(f"Model saved to {self.model_path}")
        print(f"Vectorizer saved to {self.vectorizer_path}")
    
    def load_model(self):
        """Load trained model and vectorizer"""
        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vectorizer_path)
        print("Model and vectorizer loaded successfully")
    
    def predict_emotion(self, text: str) -> Dict:
        """Predict emotion for given text"""
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
            "needs_help": needs_help,
            "probabilities": dict(zip(self.model.classes_, probabilities))
        }

def train_emotion_model():
    """Main function to train the emotion model"""
    print("Creating emotion dataset...")
    dataset = EmotionDataset()
    data = dataset.create_synthetic_dataset()
    dataset.save_dataset()
    
    print("Training emotion classification model...")
    trainer = EmotionModelTrainer()
    X, y = trainer.prepare_data(data)
    accuracy = trainer.train_model(X, y)
    
    trainer.save_model()
    print(f"Training completed with accuracy: {accuracy:.4f}")
    
    return trainer

if __name__ == "__main__":
    trainer = train_emotion_model()
    
    # Test the model
    test_texts = [
        "I am so happy today!",
        "I feel really sad and hopeless",
        "I am angry about this situation",
        "I am scared about the future",
        "This is amazing news!",
        "I am feeling okay today"
    ]
    
    print("\nTesting the model:")
    for text in test_texts:
        result = trainer.predict_emotion(text)
        print(f"Text: {text}")
        print(f"Predicted Emotion: {result['emotion']} (confidence: {result['confidence']:.3f})")
        print(f"Severity: {result['severity']}, Needs Help: {result['needs_help']}")
        print("---")
