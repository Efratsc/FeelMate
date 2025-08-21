"""
Production-Ready Emotion-Aware Supportive Chatbot
CPU-only version optimized for Core i5 CPU, 8GB RAM, HDD storage
"""

import json
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Minimal imports for CPU-only inference
from transformers import pipeline
import torch
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import LLM
from pydantic import BaseModel

class ChatMessage(BaseModel):
    """Chat message model for API requests"""
    message: str
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model for API responses"""
    response: str
    emotion: str
    severity: str
    confidence: float
    needs_help: bool
    resources: List[Dict[str, str]]
    session_id: str

class TemplateLLM(LLM):
    """Custom LLM that uses our response templates instead of external API calls"""
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Generate response using our template system"""
        # Extract emotion from the prompt (assuming it's passed in the prompt)
        emotion = self._extract_emotion_from_prompt(prompt)
        return self._generate_template_response(emotion)
    
    def _extract_emotion_from_prompt(self, prompt: str) -> str:
        """Extract emotion from the prompt text"""
        emotion_keywords = {
            'joy': ['joy', 'happy', 'excited', 'great', 'wonderful'],
            'sadness': ['sad', 'depressed', 'lonely', 'hurt'],
            'anger': ['angry', 'mad', 'furious', 'hate'],
            'fear': ['scared', 'afraid', 'worried', 'anxious'],
            'surprise': ['surprised', 'shocked', 'wow', 'unexpected'],
            'disgust': ['disgusted', 'gross', 'nasty', 'awful']
        }
        
        prompt_lower = prompt.lower()
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return emotion
        return 'neutral'
    
    def _generate_template_response(self, emotion: str) -> str:
        """Generate response using our emotion-based templates"""
        response_templates = {
            'joy': [
                "I'm so happy to hear that! Your positive energy is contagious. What made you feel this way?",
                "That's wonderful! I can feel your joy through your words. Tell me more about what's bringing you happiness!",
                "Your happiness is radiating! I'd love to hear more about what's making you feel so good."
            ],
            'sadness': [
                "I'm sorry you're feeling sad. It's okay to feel this way, and I'm here to listen. Would you like to talk more about what's on your mind?",
                "I can sense your sadness, and I want you to know that it's completely normal to feel this way sometimes. What's been weighing on your heart?",
                "I'm here to listen to whatever you need to share. Sometimes talking about our feelings can help lighten the load."
            ],
            'anger': [
                "I can understand why you'd feel angry about that. It's a natural response. Would you like to talk through what happened?",
                "Your anger is valid, and I'm here to listen. Sometimes we need to vent to process our feelings. What's been frustrating you?",
                "I can sense your frustration, and I want you to know that it's okay to feel angry. What's been building up?"
            ],
            'fear': [
                "I can sense your anxiety, and I want you to know you're not alone. Let's talk about what's worrying you.",
                "It sounds like you're experiencing some fear or anxiety. I'm here to listen and support you through this.",
                "I can hear the worry in your words. Sometimes talking about our fears can help make them feel less overwhelming."
            ],
            'surprise': [
                "That's quite unexpected! I'm here to help you process this new information. How are you feeling about it?",
                "Wow, that's surprising! I'd love to hear more about what happened and how you're processing it.",
                "That's quite a turn of events! How are you feeling about this unexpected situation?"
            ],
            'disgust': [
                "I can see why you'd feel that way. I'm here to listen and support you through this.",
                "That sounds really difficult to deal with. I'm here to listen if you want to talk about it.",
                "I can understand why you'd feel that way. Sometimes we need to process difficult emotions together."
            ],
            'neutral': [
                "I'm here to listen and support you. How are you really feeling today?",
                "I'm here for you. Sometimes it helps to talk about what's on our minds, even if we're not sure how we feel.",
                "I'm listening. What would you like to share or talk about today?"
            ]
        }
        
        import random
        if emotion in response_templates:
            return random.choice(response_templates[emotion])
        return "I'm here to listen and support you. How can I help you today?"
    
    @property
    def _llm_type(self) -> str:
        return "template_llm"

class EmotionAwareChatbot:
    """
    Production-ready emotion-aware chatbot for CPU-only inference
    Uses LangChain workflow with custom template-based LLM
    """
    
    def __init__(self):
        """Initialize the chatbot with LangChain workflow"""
        from config import MEMORY_FILE, MAX_MEMORY_MESSAGES, CRISIS_KEYWORDS
        
        self.memory_file = Path(MEMORY_FILE)
        self.conversation_memory = ConversationBufferWindowMemory(
            k=MAX_MEMORY_MESSAGES,  # Remember last N messages
            return_messages=True
        )
        
        # Use crisis keywords from config
        self.crisis_keywords = CRISIS_KEYWORDS
        
        # Load existing conversation memory
        self._load_memory()
        
        # Initialize emotion classifier (lightweight model)
        print("Loading emotion classifier...")
        try:
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=-1  # Force CPU usage
            )
            print("✅ Emotion classifier loaded successfully")
        except Exception as e:
            print(f"⚠️  Emotion classifier failed to load: {e}")
            self.emotion_classifier = None
        
        # Initialize LangChain workflow
        self._setup_langchain_workflow()
        
        print("✅ Production emotion-aware chatbot initialized successfully!")
    
    def _setup_langchain_workflow(self):
        """Setup LangChain workflow with prompts and chains"""
        
        # Create our custom template-based LLM
        self.template_llm = TemplateLLM()
        
        # Define the main conversation prompt template
        self.conversation_prompt = PromptTemplate(
            input_variables=["user_message", "emotion", "conversation_history"],
            template="""
You are FeelMate, an empathetic and supportive AI friend. Your role is to provide emotional support and understanding.

User's current emotion: {emotion}
User's message: {user_message}

Conversation history:
{conversation_history}

Based on the user's emotion and message, provide a supportive and empathetic response. 
Be genuine, caring, and helpful. Ask follow-up questions to show you care.

Response:"""
        )
        
        # Create the main conversation chain
        self.conversation_chain = LLMChain(
            llm=self.template_llm,
            prompt=self.conversation_prompt,
            memory=self.conversation_memory
        )
        
        # Crisis detection prompt template
        self.crisis_prompt = PromptTemplate(
            input_variables=["user_message"],
            template="""
Analyze the following message for crisis indicators:

User message: {user_message}

If this message contains any signs of crisis (suicide, self-harm, extreme hopelessness), 
respond with crisis intervention resources. Otherwise, respond normally.

Analysis:"""
        )
        
        # Create crisis detection chain
        self.crisis_chain = LLMChain(
            llm=self.template_llm,
            prompt=self.crisis_prompt
        )
        
        print("✅ LangChain workflow initialized successfully")
    
    def _load_memory(self):
        """Load conversation memory from JSON file"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    memory_data = json.load(f)
                    # Reconstruct conversation memory
                    for msg in memory_data.get('messages', []):
                        if msg['type'] == 'human':
                            self.conversation_memory.chat_memory.add_user_message(msg['content'])
                        elif msg['type'] == 'ai':
                            self.conversation_memory.chat_memory.add_ai_message(msg['content'])
                print(f"✅ Loaded {len(memory_data.get('messages', []))} messages from memory")
        except Exception as e:
            print(f"⚠️  Could not load memory: {e}")
    
    def _save_memory(self):
        """Save conversation memory to JSON file"""
        try:
            memory_data = {
                'last_updated': datetime.now().isoformat(),
                'messages': []
            }
            
            # Extract messages from conversation memory
            for msg in self.conversation_memory.chat_memory.messages:
                if isinstance(msg, HumanMessage):
                    memory_data['messages'].append({
                        'type': 'human',
                        'content': msg.content,
                        'timestamp': datetime.now().isoformat()
                    })
                elif isinstance(msg, AIMessage):
                    memory_data['messages'].append({
                        'type': 'ai',
                        'content': msg.content,
                        'timestamp': datetime.now().isoformat()
                    })
            
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Could not save memory: {e}")
    
    def detect_emotion(self, text: str) -> Dict[str, Any]:
        """
        Detect emotion in text using lightweight transformer model
        """
        try:
            if self.emotion_classifier:
                # Use emotion classifier
                result = self.emotion_classifier(text, top_k=1)[0]
                emotion = result['label'].lower()
                confidence = result['score']
            else:
                # Fallback to simple keyword-based emotion detection
                emotion, confidence = self._fallback_emotion_detection(text)
            
            # Map emotions to severity levels
            severity_mapping = {
                'joy': 'low',
                'surprise': 'low',
                'neutral': 'low',
                'sadness': 'medium',
                'fear': 'medium',
                'anger': 'high',
                'disgust': 'high'
            }
            
            severity = severity_mapping.get(emotion, 'medium')
            
            return {
                'emotion': emotion,
                'confidence': confidence,
                'severity': severity
            }
            
        except Exception as e:
            print(f"⚠️  Emotion detection failed: {e}")
            return {
                'emotion': 'neutral',
                'confidence': 0.5,
                'severity': 'low'
            }
    
    def _fallback_emotion_detection(self, text: str) -> tuple:
        """Simple keyword-based emotion detection as fallback"""
        text_lower = text.lower()
        
        # Simple emotion keywords
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'fantastic'],
            'sadness': ['sad', 'depressed', 'lonely', 'alone', 'miss', 'hurt', 'pain', 'crying'],
            'anger': ['angry', 'mad', 'furious', 'hate', 'annoyed', 'frustrated', 'upset'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous', 'terrified', 'panic'],
            'surprise': ['surprised', 'shocked', 'wow', 'unexpected', 'amazed', 'stunned'],
            'disgust': ['disgusted', 'gross', 'nasty', 'awful', 'terrible', 'horrible']
        }
        
        # Count keyword matches
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score
        
        # Find emotion with highest score
        if any(emotion_scores.values()):
            best_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(0.9, emotion_scores[best_emotion] * 0.3)
        else:
            best_emotion = 'neutral'
            confidence = 0.5
        
        return best_emotion, confidence
    
    def detect_crisis(self, text: str) -> bool:
        """
        Simple rule-based crisis detection
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.crisis_keywords)
    
    def generate_supportive_response(self, user_message: str, emotion: str, is_crisis: bool) -> str:
        """
        Generate supportive response using LangChain workflow
        """
        if is_crisis:
            return self._get_crisis_response()
        
        try:
            # Get conversation history for context
            conversation_history = self._get_conversation_history()
            
            # Execute LangChain conversation chain
            response = self.conversation_chain.run({
                "user_message": user_message,
                "emotion": emotion,
                "conversation_history": conversation_history
            })
            
            return response.strip()
            
        except Exception as e:
            print(f"⚠️  LangChain response generation failed: {e}")
            # Fallback to template response
            return self._get_fallback_response(emotion)
    
    def _get_crisis_response(self) -> str:
        """Get crisis intervention response"""
        return (
            "I'm very concerned about what you're sharing. "
            "If you're having thoughts of harming yourself, please know that "
            "you're not alone and help is available. "
            "Please consider reaching out to a mental health professional or "
            "contact a crisis hotline immediately:\n\n"
            "• National Suicide Prevention Lifeline (US): 988 or 1-800-273-8255\n"
            "• Crisis Text Line: Text HOME to 741741\n"
            "• Emergency Services: 911\n\n"
            "Your life has value, and there are people who want to help you."
        )
    
    def _get_conversation_history(self) -> str:
        """Get formatted conversation history for context"""
        try:
            messages = self.conversation_memory.chat_memory.messages
            if not messages:
                return "No previous conversation."
            
            history = []
            for msg in messages[-6:]:  # Last 6 messages for context
                if isinstance(msg, HumanMessage):
                    history.append(f"User: {msg.content}")
                elif isinstance(msg, AIMessage):
                    history.append(f"FeelMate: {msg.content}")
            
            return "\n".join(history)
        except Exception as e:
            print(f"⚠️  Could not get conversation history: {e}")
            return "No previous conversation."
    
    def _get_fallback_response(self, emotion: str) -> str:
        """Fallback response if LangChain fails"""
        fallback_responses = {
            'joy': "I'm so happy to hear that! Your positive energy is contagious. What made you feel this way?",
            'sadness': "I'm sorry you're feeling sad. It's okay to feel this way, and I'm here to listen. Would you like to talk more about what's on your mind?",
            'anger': "I can understand why you'd feel angry about that. It's a natural response. Would you like to talk through what happened?",
            'fear': "I can sense your anxiety, and I want you to know you're not alone. Let's talk about what's worrying you.",
            'surprise': "That's quite unexpected! I'm here to help you process this new information. How are you feeling about it?",
            'disgust': "I can see why you'd feel that way. I'm here to listen and support you through this.",
            'neutral': "I'm here to listen and support you. How are you really feeling today?"
        }
        
        return fallback_responses.get(emotion, "I'm here to listen and support you. How can I help you today?")
    
    def get_resources(self, emotion: str, severity: str) -> List[Dict[str, str]]:
        """
        Get relevant resources based on emotion and severity
        """
        resources = []
        
        if severity in ['high', 'critical']:
            resources.append({
                'name': 'Crisis Text Line',
                'url': 'https://www.crisistextline.org/',
                'description': '24/7 crisis support via text'
            })
            resources.append({
                'name': 'National Suicide Prevention Lifeline',
                'url': 'https://988lifeline.org/',
                'description': '24/7 suicide prevention support'
            })
        
        if emotion in ['sadness', 'fear']:
            resources.append({
                'name': 'BetterHelp',
                'url': 'https://www.betterhelp.com/',
                'description': 'Online therapy and counseling'
            })
        
        if emotion == 'anger':
            resources.append({
                'name': 'Anger Management Resources',
                'url': 'https://www.apa.org/topics/anger',
                'description': 'Professional anger management guidance'
            })
        
        return resources
    
    def chat(self, user_message: str, user_id: str, session_id: str = None) -> ChatResponse:
        """
        Main chat method that processes user input and returns response
        """
        # Detect emotion
        emotion_data = self.detect_emotion(user_message)
        emotion = emotion_data['emotion']
        confidence = emotion_data['confidence']
        severity = emotion_data['severity']
        
        # Detect crisis
        is_crisis = self.detect_crisis(user_message)
        
        # Generate response using LangChain workflow
        response = self.generate_supportive_response(user_message, emotion, is_crisis)
        
        # Update conversation memory
        self.conversation_memory.chat_memory.add_user_message(user_message)
        self.conversation_memory.chat_memory.add_ai_message(response)
        
        # Save memory to file
        self._save_memory()
        
        # Get resources if needed
        needs_help = is_crisis or severity in ['high', 'critical']
        resources = self.get_resources(emotion, severity) if needs_help else []
        
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"
        
        return ChatResponse(
            response=response,
            emotion=emotion,
            severity=severity,
            confidence=confidence,
            needs_help=needs_help,
            resources=resources,
            session_id=session_id
        )

# Global chatbot instance
chatbot = EmotionAwareChatbot()

def get_chatbot():
    """Get the global chatbot instance"""
    return chatbot
