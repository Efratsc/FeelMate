#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration settings for FeelMate Backend
"""

# Session Management
SESSION_TIMEOUT_MINUTES = 30  # Sessions expire after 30 minutes of inactivity
SESSION_CLEANUP_INTERVAL_HOURS = 24  # Clean up old sessions every 24 hours

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8001

# Database Configuration
DATABASE_URL = None  # Will be loaded from .env file

# Emotion Classification
EMOTION_CONFIDENCE_THRESHOLD = 0.3  # Minimum confidence for emotion classification
MAX_CONVERSATION_HISTORY = 10  # Number of recent messages to consider for context

# Crisis Detection
CRISIS_PHRASES = [
    'kill myself', 'kill my self', 'want to die', 'end my life', 'end it all',
    'no reason to live', 'better off dead', 'hurt myself', 'self harm',
    'suicide', 'give up', 'cant take it anymore', 'wanna kill', 'want to kill'
]

# Resource URLs
CRISIS_RESOURCES = [
    {
        "title": "National Suicide Prevention Lifeline",
        "description": "24/7 crisis support",
        "url": "https://988lifeline.org/",
        "phone": "988",
        "type": "crisis"
    },
    {
        "title": "Crisis Text Line",
        "description": "Text-based crisis support",
        "url": "https://www.crisistextline.org/",
        "text": "HOME to 741741",
        "type": "crisis"
    },
    {
        "title": "Find a Therapist",
        "description": "Professional mental health support",
        "url": "https://www.psychologytoday.com/us/therapists",
        "type": "therapy"
    }
]


