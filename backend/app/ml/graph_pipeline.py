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
import random
import re
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

        # Minimal curated therapist directory (sample data)
        self.therapist_directory = [
            {"name": "Psychology Today Directory", "city": "Global", "focus": ["directory","therapist"], "url": "https://www.psychologytoday.com/us/therapists"},
            {"name": "TherapyDen Directory", "city": "Global", "focus": ["directory","inclusive"], "url": "https://www.therapyden.com/therapists"},
            {"name": "Find a Helpline", "city": "Global", "focus": ["crisis","support"], "url": "https://findahelpline.com/"},
            {"name": "NAMI HelpLine", "city": "US", "focus": ["support","education"], "url": "https://www.nami.org/help"},
            {"name": "NHS Talking Therapies", "city": "UK", "focus": ["cbt","talking therapies"], "url": "https://www.nhs.uk/service-search/mental-health/find-an-NHS-talking-therapies-service"},
            # Ethiopia-specific
            {"name": "Sitota Psychological Services", "city": "Addis Ababa", "focus": ["counseling","therapy"], "url": "https://sitotapsy.com"},
            {"name": "Aha Psychological Services", "city": "Addis Ababa", "focus": ["assessment","therapy"], "url": "https://www.ahaethiopia.com"},
            {"name": "Abrihot Specialized Psychological Center", "city": "Addis Ababa", "focus": ["psychology","counseling"], "url": "https://abrihot.com"},
        ]

        # Simple intent triggers for therapist-finder
        self.therapist_intent_phrases = [
            "find therapist", "find a therapist", "therapist near me",
            "counselor near me", "find counselor", "find a counselor",
            "how do i find a therapist", "recommend therapist", "therapy options"
        ]

        # Common typo/normalization map
        self._normalize_map = {
            "colligues": "colleagues",
            "collegue": "colleague",
            "collague": "colleague",
            "deadlines": "deadline",
            "parents": "family",
            "mom": "family",
            "dad": "family",
            "boyfriend": "partner",
            "girlfriend": "partner",
            "yeah": "yes"
        }

    def _extract_key_phrases(self, text: str, limit: int = 2) -> List[str]:
        """Very lightweight key phrase extraction without LLMs.
        - Prefers words around common markers (work, family, friends, school, money, health)
        - Falls back to longest unique words (length >= 4)
        """
        t = (text or "").lower()
        if not t:
            return []

        topical_markers = [
            "work", "job", "boss", "family", "parents", "mom", "dad", "friend",
            "relationship", "school", "study", "college", "money", "bills", "health",
            "exam", "grades", "breakup", "deadline", "colleague", "teacher"
        ]

        phrases: List[str] = []
        for marker in topical_markers:
            if marker in t:
                phrases.append(self._normalize_map.get(marker, marker))

        # fallback: longest unique words
        if len(phrases) < limit:
            words = [re.sub(r"^[^a-zA-Z]+|[^a-zA-Z]+$", "", w) for w in t.split()]
            words = [w for w in words if len(w) >= 4 and w.isalpha()]
            # de-dup preserving order
            seen = set()
            unique_words: List[str] = []
            for w in words:
                # normalize typos/plurals
                w = self._normalize_map.get(w, w)
                if w.endswith("s") and len(w) > 4:
                    w = w[:-1]
                if w not in seen:
                    seen.add(w)
                    unique_words.append(w)
            # sort by length desc to bias toward more informative words
            unique_words.sort(key=len, reverse=True)
            for w in unique_words:
                if w not in phrases:
                    phrases.append(w)
                if len(phrases) >= limit:
                    break

        return phrases[:limit]

    def _reflective_line(self, text: str, emotion: str, session_id: str) -> str:
        """Compose a short reflective sentence leveraging key phrases and recent context.
        Avoid repetition if the last assistant message already reflected on the same phrase.
        """
        key_phrases = self._extract_key_phrases(text, limit=2)
        context = self._get_conversation_context(session_id, limit=2)
        recent_topic = None
        for msg in reversed(context):
            candidate = self._extract_key_phrases(msg.get("user", ""), limit=1)
            if candidate:
                recent_topic = candidate[0]
                break

        # If last assistant already reflected with the same phrase, skip
        if context:
            last_assistant = context[-1].get("assistant", "").lower()
            if any(p in (last_assistant or "") for p in key_phrases):
                return ""

        openings_by_emotion = {
            "sad": [
                "I can hear the sadness in this.",
                "This sounds really heavy.",
                "I'm hearing a lot of pain here."
            ],
            "anxious": [
                "I hear the worry in this.",
                "That sounds really tense.",
                "This seems really stressful."
            ],
            "angry": [
                "I can hear your frustration.",
                "That sounds upsetting and unfair.",
                "I hear how strongly you feel about this."
            ],
            "happy": [
                "I love hearing this.",
                "That’s great to hear.",
                "I’m glad things are looking up."
            ],
            "neutral": [
                "Thanks for sharing.",
                "I’m here with you.",
                "I’m listening."
            ]
        }
        opening = random.choice(openings_by_emotion.get(emotion, openings_by_emotion["neutral"]))

        if key_phrases and recent_topic and recent_topic in key_phrases:
            return f"{opening} It sounds like you're still feeling {emotion} about {recent_topic}."
        elif key_phrases:
            if len(key_phrases) == 1:
                return f"{opening} I hear {emotion} in what you said about {key_phrases[0]}."
            return f"{opening} I hear {emotion} in what you said about {key_phrases[0]} and {key_phrases[1]}."
        else:
            return f"{opening} I hear you're feeling {emotion}."

    def _actionable_nudge(self, text: str, emotion: str, severity: str) -> str:
        if severity not in ("medium", "high"):
            return ""
        phrases = self._extract_key_phrases(text, limit=1)
        topic = phrases[0] if phrases else None
        suggestions_generic = [
            "Would it help to jot down the top 1–2 things bothering you?",
            "Would taking a short break or a few slow breaths help right now?",
            "Could it help to text someone you trust about this?"
        ]
        topic_suggestions = {
            "work": "Would it help to list what's changed and what you need from your boss?",
            "deadline": "Could you list the tasks and pick the smallest next step?",
            "family": "Would it help to write what you wish you could say to them?",
            "relationship": "Could it help to draft how you'd like to express your needs?",
            "money": "Would a 10‑minute plan on bills and dates help reduce the fog?",
            "health": "Would checking in on rest, water, or a brief stretch help?"
        }
        if topic and topic in topic_suggestions:
            return " " + topic_suggestions[topic]
        return " " + random.choice(suggestions_generic)

    # ---- Therapist finder tool helpers ----
    def _detect_therapist_intent(self, text: str) -> bool:
        t = (text or "").lower()
        return any(p in t for p in self.therapist_intent_phrases)

    def _tool_find_therapists(self, text: str, limit: int = 5) -> list:
        t = (text or "").lower()
        hits = []
        for item in self.therapist_directory:
            city_hit = item["city"].lower() in t
            focus_hit = any(f.lower() in t for f in item["focus"])
            generic_hit = any(k in t for k in ["therapist", "counselor", "therapy"])
            if city_hit or focus_hit or generic_hit:
                hits.append(item)
        unique = []
        seen = set()
        for h in hits:
            key = (h["name"], h["city"])
            if key not in seen:
                seen.add(key)
                unique.append(h)
            if len(unique) >= limit:
                break
        return unique

    def _format_therapist_results(self, results: list) -> str:
        if not results:
            return ("I couldn’t find specific matches right now. "
                    "You might try ‘find therapist in <your city>’ or include a focus like ‘CBT’ or ‘depression’.")
        lines = ["Here are a few options you could consider:"]
        for r in results:
            focus_str = ", ".join(r["focus"])
            lines.append(f"- {r['name']} — {r['city']} — focus: {focus_str} — {r['url']}")
        lines.append("If any of these look helpful, you can visit their links or search similar providers nearby.")
        return "\n".join(lines)

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
            text_lower = (text or "").lower()

            # Heuristic neutral intents override (small-talk/unsure/opening)
            neutral_markers = [
                "not sure what i feel",
                "not sure how i feel",
                "i'm not sure how i feel",
                "i dont know where to start",
                "i don't know where to start",
                "can we just chat",
                "can we just talk",
                "i needed to talk",
                "i need to talk",
                "just chat",
                "just talk"
            ]
            if any(m in text_lower for m in neutral_markers):
                return "neutral"
            
            # If confidence is low, try keyword-based detection as backup
            if confidence < 0.6:
                if any(w in text_lower for w in ["sad", "down", "depressed", "unhappy", "crying"]):
                    return "sad"
                elif any(w in text_lower for w in ["angry", "mad", "frustrated", "upset", "hate"]):
                    return "angry"
                elif any(w in text_lower for w in ["anxious", "worried", "stressed", "nervous"]):
                    return "anxious"
                elif any(w in text_lower for w in ["happy", "good", "great", "wonderful"]):
                    return "happy"
                # Low-confidence fallback to neutral if unsure/opening language
                if any(m in text_lower for m in neutral_markers):
                    return "neutral"
            
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

    def _generate_contextual_response(self, emotion: str, text: str, session_id: str, severity: str) -> str:
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

        # Fall back to the original template response, but prepend a reflective line
        base = self._template_response(emotion, text)
        reflection = self._reflective_line(text, emotion, session_id)
        nudge = self._actionable_nudge(text, emotion, severity)
        combined = (reflection + " " + base + nudge).strip()
        return combined

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

        # Tool intent: therapist finder (runs before emotion logic to avoid delays)
        if self._detect_therapist_intent(user_text):
            results = self._tool_find_therapists(user_text, limit=5)
            response = self._format_therapist_results(results)
            self._save_conversation(session_id, user_text, response, "neutral")
            return GraphResult(
                response=response,
                emotion="neutral",
                severity="low",
                crisis_detected=False,
                session_id=session_id,
                confidence=0.8,
                needs_help=True,
                resources=self.resources["general"],
            )

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
            response = self._generate_contextual_response(emotion, user_text, session_id, severity)

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


