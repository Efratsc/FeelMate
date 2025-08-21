"""
Production configuration for FeelMate Emotion-Aware Chatbot
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8001))

# Model Configuration
EMOTION_MODEL = os.getenv("EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base")
DEVICE = os.getenv("DEVICE", "cpu")

# Memory Configuration
MEMORY_FILE = os.getenv("MEMORY_FILE", "data/conversation_memory.json")
MAX_MEMORY_MESSAGES = int(os.getenv("MAX_MEMORY_MESSAGES", 5))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/chatbot.log")

# Frontend Configuration
FRONTEND_URLS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# Crisis Detection Configuration
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "hopeless", "worthless", "no reason to live", "better off dead",
    "self-harm", "cut myself", "overdose", "harm myself",
    "can't take it anymore", "life is meaningless"
]

# Production Settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
RELOAD = DEBUG  # Only reload in debug mode


