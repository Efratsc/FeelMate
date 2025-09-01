"""
LLM-free LangGraph pipeline for FeelMate.
Coordinates: emotion classification (HuggingFace), crisis detection (rules),
memory retrieval (PostgresConversationMemory), and empathetic template generation.
Outputs align with ChatResponse schema used by the server.
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from dataclasses import dataclass

from transformers import pipeline

# Memory for conversation persistence (in-memory for simplicity)
from typing import List, Dict
import json


@dataclass
class GraphResult:
    response: str
    emotion: str
    severity: str
    crisis_detected: bool
    session_id: str
    confidence: float = 0.8
    needs_help: bool = False
    resources: list = None


class FeelMateGraph:
    def __init__(self) -> None:
        self.emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=-1,
        )
        
        # In-memory conversation storage
        self.conversation_memory: Dict[str, List[Dict[str, str]]] = {}
        # Enhanced crisis detection
        self.crisis_keywords = {
            "suicide","suicidal","end my life","take my life","want to die","kill myself","self-harm","self harm",
            "unalive","unalive myself","kys","end it all","no reason to live","better off dead"
        }
        
        # Help-seeking indicators
        self.help_keywords = {
            "help","support","therapy","counselor","psychologist","mental health","crisis","emergency"
        }
        
        # Resource recommendations
        self.resources = {
            "crisis": [
                {"name": "National Suicide Prevention Lifeline", "url": "https://suicidepreventionlifeline.org", "description": "Call 988 for immediate support"},
                {"name": "Crisis Text Line", "url": "https://www.crisistextline.org", "description": "Text HOME to 741741"},
                {"name": "Emergency Services", "url": "tel:911", "description": "Call 911 if in immediate danger"}
            ],
            "general": [
                {"name": "National Alliance on Mental Illness", "url": "https://www.nami.org", "description": "Mental health support and resources"},
                {"name": "Psychology Today", "url": "https://www.psychologytoday.com", "description": "Find therapists and counselors"},
                {"name": "BetterHelp", "url": "https://www.betterhelp.com", "description": "Online therapy platform"}
            ]
        }

    def _detect_emotion(self, text: str) -> str:
        result = self.emotion_classifier(text or "")
        if result:
            # Map the model's output to our emotion categories
            emotion = result[0]["label"].lower()
            confidence = result[0]["score"]
            
            # Map model emotions to our categories
            emotion_map = {
                "sadness": "sad",
                "fear": "anxious", 
                "anger": "angry",
                "joy": "happy",
                "surprise": "surprised",
                "disgust": "disgusted",
                "neutral": "neutral"
            }
            
            mapped_emotion = emotion_map.get(emotion, "neutral")
            
            # If confidence is low, try keyword-based detection as backup
            if confidence < 0.6:
                text_lower = (text or "").lower()
                if any(w in text_lower for w in ["sad", "down", "depressed", "unhappy", "crying"]):
                    return "sad"
                elif any(w in text_lower for w in ["angry", "mad", "frustrated", "upset", "hate"]):
                    return "angry"
                elif any(w in text_lower for w in ["anxious", "worried", "stressed", "nervous"]):
                    return "anxious"
                elif any(w in text_lower for w in ["happy", "good", "great", "wonderful"]):
                    return "happy"
            
            return mapped_emotion
        return "neutral"

    def _detect_crisis(self, text: str) -> bool:
        normalized = (text or "").lower()
        return any(k in normalized for k in self.crisis_keywords)
    
    def _detect_help_seeking(self, text: str) -> bool:
        normalized = (text or "").lower()
        return any(k in normalized for k in self.help_keywords)
    
    def _get_resources(self, crisis: bool, help_seeking: bool) -> list:
        if crisis:
            return self.resources["crisis"]
        elif help_seeking:
            return self.resources["general"]
        return []

    def _severity_from_crisis(self, crisis: bool, emotion: str, text: str) -> str:
        if crisis:
            return "high"
        
        # More nuanced severity based on emotion and content
        text_lower = (text or "").lower()
        
        # High severity indicators
        high_severity_words = ["hate", "despise", "worthless", "hopeless", "can't take it", "breaking down", "falling apart"]
        if any(w in text_lower for w in high_severity_words):
            return "high"
        
        # Medium severity indicators  
        medium_severity_words = ["really sad", "very upset", "so angry", "extremely", "terrible", "awful", "horrible"]
        if any(w in text_lower for w in medium_severity_words):
            return "medium"
        
        # Emotion-based severity
        if emotion in ["sad", "angry", "anxious"]:
            return "medium"
        elif emotion in ["happy", "neutral"]:
            return "low"
        
        return "low"

    def _get_conversation_context(self, session_id: str, limit: int = 5) -> List[Dict[str, str]]:
        """Get recent conversation history for context"""
        if session_id not in self.conversation_memory:
            return []
        return self.conversation_memory[session_id][-limit:]

    def _save_conversation(self, session_id: str, user_message: str, assistant_response: str, emotion: str):
        """Save conversation to memory"""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        
        self.conversation_memory[session_id].append({
            "user": user_message,
            "assistant": assistant_response,
            "emotion": emotion,
            "timestamp": __import__('time').time()
        })
        
        # Keep only last 20 messages to prevent memory bloat
        if len(self.conversation_memory[session_id]) > 20:
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-20:]

    def _generate_contextual_response(self, emotion: str, text: str, session_id: str) -> str:
        """Generate response using conversation context"""
        context = self._get_conversation_context(session_id)
        t = (text or "").lower()
        
        # Check for conversation continuity
        if context:
            last_emotion = context[-1].get("emotion", "neutral")
            last_user_msg = context[-1].get("user", "").lower()
            
            # If user is continuing a previous topic
            if any(word in t for word in ["yes", "no", "maybe", "i think", "i feel", "it's", "that's"]):
                if emotion == "sad" and last_emotion == "sad":
                    return "I can see this is really weighing on you. It sounds like you've been dealing with this for a while. What's been the hardest part?"
                elif emotion == "angry" and last_emotion == "angry":
                    return "I hear how frustrated you still are about this. Sometimes when we're angry, it helps to talk through what we wish we could do differently. What's been on your mind?"
                elif emotion == "anxious" and last_emotion == "anxious":
                    return "I can tell this anxiety is really persistent. What's been making you feel most worried since we last talked?"
        
        # Check for topic continuation
        if context:
            recent_topics = []
            for msg in context[-3:]:  # Last 3 messages
                user_msg = msg.get("user", "").lower()
                if "work" in user_msg or "job" in user_msg:
                    recent_topics.append("work")
                elif "family" in user_msg or "parents" in user_msg or "mom" in user_msg or "dad" in user_msg:
                    recent_topics.append("family")
                elif "friend" in user_msg or "relationship" in user_msg:
                    recent_topics.append("relationships")
                elif "school" in user_msg or "study" in user_msg or "college" in user_msg:
                    recent_topics.append("school")
            
            # If continuing a topic
            if "work" in recent_topics and any(w in t for w in ["work", "job", "boss", "colleague"]):
                if emotion == "sad":
                    return "It sounds like work is really affecting your mood. What's been happening there that's making you feel this way?"
                elif emotion == "angry":
                    return "Work stress can be so frustrating. What's been the most difficult part of your work situation?"
            
            elif "family" in recent_topics and any(w in t for w in ["family", "parents", "mom", "dad", "sister", "brother"]):
                if emotion == "sad":
                    return "Family relationships can be so complicated and hurtful. What's been happening with your family that's making you feel this way?"
                elif emotion == "angry":
                    return "Family conflicts can be incredibly frustrating. What's been the most upsetting part of your family situation?"
            
            elif "relationships" in recent_topics and any(w in t for w in ["friend", "relationship", "boyfriend", "girlfriend", "partner"]):
                if emotion == "sad":
                    return "Relationship problems can be so painful. What's been happening in your relationships that's making you feel this way?"
                elif emotion == "angry":
                    return "Relationship conflicts can be really frustrating. What's been bothering you about your relationships?"

        # Fall back to the original template response
        return self._template_response(emotion, text)

    def _template_response(self, emotion: str, text: str) -> str:
        t = (text or "").lower()
        
        # Specific context-aware responses for common situations
        if any(w in t for w in ["insulted", "insults", "bullied", "teased", "made fun of"]):
            if emotion == "sad":
                return "I'm so sorry you're being treated this way. No one deserves to be insulted or bullied. How long has this been happening?"
            elif emotion == "angry":
                return "That's completely understandable - being insulted is hurtful and frustrating. What's been the hardest part to deal with?"
            else:
                return "Being insulted can really hurt. I'm here to listen if you want to talk about what's been happening."
        
        if any(w in t for w in ["hate", "hate me", "everyone hates", "nobody likes"]):
            if emotion == "sad":
                return "I hear how much this is hurting you. When we feel like everyone hates us, it can feel so isolating. Can you tell me more about what's making you feel this way?"
            elif emotion == "angry":
                return "Feeling like everyone hates you can be incredibly frustrating and painful. What's been happening that's making you feel this way?"
            else:
                return "That sounds really painful. Sometimes our minds can make us feel more alone than we actually are. What's been going on?"
        
        if any(w in t for w in ["sad", "down", "depressed", "unhappy", "crying", "tears"]):
            responses = [
                "I can hear the sadness in your words. It takes courage to share when you're feeling down. What's been weighing on your heart?",
                "Feeling sad can be so heavy and isolating. You're not alone in this - I'm here to listen. What's been on your mind?",
                "That sounds really difficult. Sometimes when we're sad, it helps to talk about what's making us feel this way. What's been bothering you?"
            ]
            return responses[hash(text) % len(responses)]
            
        if any(w in t for w in ["anxious", "worried", "stressed", "nervous", "panic", "overwhelmed"]):
            responses = [
                "Anxiety can feel so overwhelming and exhausting. What's been making you feel most worried or stressed?",
                "I can hear the stress in your words. Sometimes it helps to break down what's feeling most overwhelming. What's on your mind?",
                "That sounds really stressful. Anxiety can make everything feel bigger and scarier. What would help you feel more grounded right now?"
            ]
            return responses[hash(text) % len(responses)]
            
        if any(w in t for w in ["angry", "mad", "frustrated", "upset", "annoyed", "irritated"]):
            responses = [
                "I can hear your frustration and anger. Those feelings are completely valid. What happened that's making you feel this way?",
                "That sounds really frustrating and upsetting. Sometimes anger is our way of protecting ourselves. What's been bothering you?",
                "I hear how upset you are. Anger can be so intense and overwhelming. What's been making you feel this way?"
            ]
            return responses[hash(text) % len(responses)]
            
        if any(w in t for w in ["lonely", "alone", "isolated", "empty", "nobody cares"]):
            responses = [
                "Feeling lonely can be one of the hardest emotions to bear. You're not alone in feeling this way. What's been making you feel isolated?",
                "Loneliness can feel so heavy and overwhelming. I'm here to listen if you want to share what's been on your mind.",
                "That sounds really painful. Sometimes when we feel alone, it helps to remember that there are people who care. What's been going on?"
            ]
            return responses[hash(text) % len(responses)]
            
        if any(w in t for w in ["tired", "exhausted", "burned out", "drained", "can't cope"]):
            responses = [
                "That sounds absolutely exhausting. Burnout can make everything feel impossible. What's been draining your energy the most?",
                "I hear how tired and drained you are. Sometimes we need to rest and recharge. What's been taking up most of your energy?",
                "That sounds overwhelming. When we're exhausted, even small things can feel too much. What's been going on?"
            ]
            return responses[hash(text) % len(responses)]
        
        # Emotion-based responses with more empathy and specificity
        emotion_responses = {
            "sad": [
                "I can hear the sadness in your words. It takes strength to share when you're feeling down. What's been weighing on your heart?",
                "That sounds really difficult. Sometimes when we're sad, it helps to talk about what's making us feel this way. What's been bothering you?",
                "I'm here with you. Sadness can feel so heavy and isolating. What's been on your mind?"
            ],
            "anxious": [
                "I can hear the anxiety in your words. That must feel really overwhelming. What's been making you feel most worried?",
                "Anxiety can be so exhausting and scary. Sometimes it helps to talk through what's feeling most overwhelming. What's on your mind?",
                "That sounds really stressful. Anxiety can make everything feel bigger and more frightening. What would help you feel more grounded?"
            ],
            "angry": [
                "I hear your anger and frustration. Those feelings are completely valid. What happened that's making you feel this way?",
                "That sounds really frustrating and upsetting. Sometimes anger is our way of protecting ourselves. What's been bothering you?",
                "I can hear how upset you are. Anger can be so intense and overwhelming. What's been making you feel this way?"
            ],
            "happy": [
                "I'm so glad to hear that! It's wonderful when things are going well. What's been bringing you joy lately?",
                "That sounds amazing! It's great to hear some positivity. What's been making you feel happy?",
                "I love hearing that! What's been going well for you recently?"
            ],
            "surprised": [
                "That sounds unexpected! Surprises can be exciting or overwhelming. How are you feeling about it?",
                "Wow, that sounds like quite a surprise! What happened that caught you off guard?",
                "That must have been quite a shock! How are you processing what happened?"
            ],
            "disgusted": [
                "That sounds really unpleasant and upsetting. What happened that's making you feel this way?",
                "I can hear how upsetting that is. Sometimes disgust is our way of protecting ourselves. What's been going on?",
                "That sounds really difficult to deal with. What's been bothering you?"
            ],
            "neutral": [
                "Thanks for sharing. I'm here to listen. What would you like to talk about?",
                "I'm here with you. What's been on your mind today?",
                "Thanks for reaching out. How can I support you right now?"
            ]
        }
        
        responses = emotion_responses.get(emotion, [
            "I'm here with you. What would you like to talk about?",
            "Thanks for sharing. How can I support you today?",
            "I'm listening. What's been on your mind?"
        ])
        
        # Use text hash to select response for consistency
        return responses[hash(text) % len(responses)]

    def run(self, *, user_text: str, user_id: str, session_id: Optional[str]) -> GraphResult:
        # Ensure session (simplified for LangGraph mode)
        if not session_id:
            session_id = f"langgraph_{user_id}_{int(__import__('time').time())}"

        # Nodes: emotion/crisis/help detection
        emotion = self._detect_emotion(user_text)
        crisis = self._detect_crisis(user_text)
        help_seeking = self._detect_help_seeking(user_text)
        severity = self._severity_from_crisis(crisis, emotion, user_text)
        resources = self._get_resources(crisis, help_seeking)
        


        if crisis:
            response = (
                "I'm really glad you told me. Your safety matters. Please reach out right now: "
                "In the US call/text 988, text HOME to 741741, or call local emergency services. "
                "If you're outside the US, visit findahelpline.com for resources."
            )
        else:
            # Use contextual response generation
            response = self._generate_contextual_response(emotion, user_text, session_id)

        # Save conversation to memory for context
        self._save_conversation(session_id, user_text, response, emotion)

        return GraphResult(
            response=response,
            emotion=emotion,
            severity=severity,
            crisis_detected=crisis,
            session_id=session_id,
            confidence=0.8,
            needs_help=help_seeking or crisis,
            resources=resources,
        )
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get full conversation history for a session"""
        return self.conversation_memory.get(session_id, [])
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_memory:
            del self.conversation_memory[session_id]


_graph_instance: Optional[FeelMateGraph] = None


def get_graph() -> FeelMateGraph:
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = FeelMateGraph()
    return _graph_instance


