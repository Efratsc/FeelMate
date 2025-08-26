import os
import re
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from pydantic import BaseModel

# Import our custom PostgreSQL memory implementation
from postgres_memory import PostgresConversationMemory, get_or_create_session
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

# --- Pydantic models ---
class ChatResponse(BaseModel):
    response: str
    emotion: str
    severity: str = None
    crisis_detected: bool = False
    session_id: str = None

class ChatMessage(BaseModel):
    role: str
    content: str

# --- Emotion-Aware Chatbot with PostgreSQL LangChain Memory ---
class EmotionAwareChatbot:
    def __init__(self):
        # GPT-2 LLM wrapped with LangChain
        print("Loading GPT-2 LLM...")
        gpt2_pipeline = pipeline(
            "text-generation",
            model="distilgpt2",
            device=-1,
            max_new_tokens=150,
            pad_token_id=50256,
            do_sample=True,
            top_p=0.9,
            temperature=0.7
        )
        self.gpt2_llm = HuggingFacePipeline(pipeline=gpt2_pipeline)
        print("✅ GPT-2 loaded")

        # LangChain prompt template with warm, concise guidance
        self.prompt_template = PromptTemplate(
            input_variables=["history", "user_message", "emotion", "session_context"],
            template=(
                "You are FeelMate, a supportive AI friend. Be warm, validating, and concise.\n"
                "Guidelines: 1-3 sentences, no lists, no repeating words, reflect their feeling, ask a gentle follow-up.\n"
                "Detected emotion: {emotion}. Context: {session_context}.\n\n"
                "Conversation so far:\n{history}\n\n"
                "User: {user_message}\n"
                "FeelMate: "
            )
        )

        # Emotion classifier
        print("Loading emotion classifier...")
        self.emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=-1
        )
        print("✅ Emotion classifier loaded")

        # Crisis keywords and patterns (including common misspellings/variants)
        self.crisis_keywords = [
            "suicide", "commit suicide", "suicidal", "end my life", "take my life",
            "want to die", "no reason to live", "better off dead", "hurt myself",
            "self-harm", "self harm", "give up", "cant take it anymore", "can't take it anymore",
            "thinking about ending", "don't want to live", "do not want to live",
            "want to disappear", "no point in living", "end it all", "unalive", "unalive myself",
            "kill myself", "kill my self", "kys"
        ]
        # Regex patterns to catch separated or obfuscated wording
        self.crisis_patterns = [
            r"kill\s+my\s+self",              # kill my self
            r"kill\s+myself",                 # kill     myself
            r"end\s+my\s+life",
            r"take\s+my\s+life",
            r"want\s+to\s+die",
            r"no\s+reason\s+to\s+live",
            r"no\s+point\s+in\s+living",
            r"self\s*-?\s*harm",
            r"do(n'?|\s*no)t\s+want\s+to\s+live",
            r"end\s+it\s+all",
        ]

        print("✅ Emotion-aware chatbot initialized with PostgreSQL memory!")

    # --- Emotion detection ---
    def _detect_emotion(self, message):
        result = self.emotion_classifier(message)
        return result[0]["label"] if result else "neutral"

    def _smooth_emotion(self, message_text: str, detected: str) -> str:
        """Heuristic smoothing to avoid mismatched labels (e.g., joy for negative text)."""
        text = (message_text or "").lower()
        negative_markers = [
            "sad", "down", "hurt", "angry", "mad", "anxious", "afraid", "scared",
            "not good enough", "insulted", "ashamed", "guilty", "lonely", "tired", "overwhelmed"
        ]
        positive_markers = ["happy", "joy", "excited", "grateful", "proud"]
        has_negative = any(k in text for k in negative_markers)
        has_positive = any(k in text for k in positive_markers)
        if has_negative and not has_positive and detected == "joy":
            return "sadness"
        return detected

    # --- Crisis detection ---
    def _detect_crisis(self, message):
        text = (message or "").lower()
        normalized = " ".join(text.split())
        # Simple keyword hit
        if any(keyword in normalized for keyword in self.crisis_keywords):
            return True
        # Regex pattern hit
        for pattern in self.crisis_patterns:
            if re.search(pattern, normalized):
                return True
        return False

    # --- Get session context for enhanced responses ---
    def _get_session_context(self, memory: PostgresConversationMemory) -> str:
        """Get session context for enhanced prompt generation"""
        session_info = memory.get_session_info()
        if not session_info:
            return "New conversation session"
        
        context_parts = []
        if session_info.get('current_emotion'):
            context_parts.append(f"Recent emotion: {session_info['current_emotion']}")
        if session_info.get('severity_level'):
            context_parts.append(f"Severity: {session_info['severity_level']}")
        if session_info.get('message_count', 0) > 0:
            context_parts.append(f"Conversation length: {session_info['message_count']} messages")
        
        return "; ".join(context_parts) if context_parts else "Ongoing conversation"

    # --- Main chat function with PostgreSQL LangChain Memory ---
    def chat(self, user_message, user_id, session_id=None):
        # Get or create session
        session_id = get_or_create_session(user_id, session_id)
        
        # Initialize PostgreSQL-based LangChain memory
        memory = PostgresConversationMemory(
            session_id=session_id,
            user_id=user_id,
            max_messages=10
        )
        
        # Detect emotion and smooth
        emotion = self._detect_emotion(user_message)
        emotion = self._smooth_emotion(user_message, emotion)
        
        # Detect crisis
        crisis_detected = self._detect_crisis(user_message)
        if crisis_detected:
            # Override emotion label to reflect urgency in downstream displays
            emotion = "distress"
        
        # Get session context
        session_context = self._get_session_context(memory)
        
        # Get conversation history from LangChain memory
        history_messages = memory.chat_memory._messages
        history_text = ""
        last_user_text = ""
        if history_messages:
            # Convert LangChain messages to text format
            history_lines = []
            for msg in history_messages[-6:]:  # Last 6 messages for context
                if hasattr(msg, 'content'):
                    if isinstance(msg, HumanMessage):
                        history_lines.append(f"User: {msg.content}")
                        last_user_text = msg.content
                    elif isinstance(msg, AIMessage):
                        history_lines.append(f"AI: {msg.content}")
            history_text = "\n".join(history_lines)

        # If current detection is neutral but prior user text likely negative, borrow that signal
        if emotion == "neutral" and last_user_text:
            prev_detected = self._smooth_emotion(last_user_text, self._detect_emotion(last_user_text))
            if prev_detected != "neutral":
                emotion = prev_detected
        
        # Prepare prompt with enhanced context
        prompt_text = self.prompt_template.format(
            history=history_text,
            user_message=user_message,
            emotion=emotion,
            session_context=session_context
        )
        
        # Try to generate response using GPT-2, but fall back to templates if it fails
        ai_response = ""
        try:
            # Generate response using LangChain
            llm_chain = LLMChain(
                llm=self.gpt2_llm, 
                prompt=PromptTemplate(
                    input_variables=["text"], 
                    template="{text}"
                )
            )
            
            ai_result = llm_chain.invoke({"text": prompt_text})
            
            # Extract the actual text from LangChain result
            if hasattr(ai_result, 'content'):
                ai_response = ai_result.content
            elif hasattr(ai_result, 'text'):
                ai_response = ai_result.text
            elif isinstance(ai_result, dict) and 'text' in ai_result:
                ai_response = ai_result['text']
            else:
                ai_response = str(ai_result)
            
            ai_response = ai_response.strip()
            
            # Clean up response - remove prompt text and get only the response
            if "FeelMate:" in ai_response:
                ai_response = ai_response.split("FeelMate:")[-1].strip()
            if "Respond supportively" in ai_response:
                ai_response = ai_response.split("Respond supportively")[0].strip()
            
            # Remove any remaining prompt text
            if "User:" in ai_response:
                ai_response = ai_response.split("User:")[0].strip()
            if "Conversation history:" in ai_response:
                ai_response = ai_response.split("Conversation history:")[0].strip()
            
            # Clean up repetitive words/phrases and emotion echoes like "anger, anger"
            def _dedupe_repeats(text: str) -> str:
                # Collapse repeated words (up to 3 times) and comma-separated repeats
                import re as _re
                # e.g., anger, anger, anger -> anger
                text = _re.sub(r"\b(\w+)(?:\s*,\s*\1\b)+", r"\1", text, flags=_re.IGNORECASE)
                # e.g., anger anger anger -> anger
                text = _re.sub(r"\b(\w+)(?:\s+\1\b){1,}\b", r"\1", text, flags=_re.IGNORECASE)
                # Remove redundant underscores or leading artifacts
                text = _re.sub(r"^[_\-\s]+", "", text)
                return text.strip()

            ai_response = _dedupe_repeats(ai_response)
            
            # If the whole chunk repeats, trim
            if len(ai_response) >= 50 and ai_response.count(ai_response[:50]) > 1:
                ai_response = ai_response[:200].rstrip() + "..."
            
            # Additional quality filters for GPT-2 outputs
            def _looks_low_quality(text: str) -> bool:
                t = (text or "").lower()
                bad_fragments = [
                    "i've never heard of it",
                    "ive never heard of it",
                    "feelmate",  # hallucinating name often in odd contexts
                    "feel ",     # clipped token often appears as "feel"
                    "http://", "https://",  # prevent random links from gpt2
                    "as an ai", "language model"
                ]
                if any(bad in t for bad in bad_fragments):
                    return True
                if len(t.split()) <= 3:
                    return True
                # Too many repeated characters
                if re.search(r"(.)\1{4,}", t):
                    return True
                return False

            # Check if GPT-2 response is usable
            if (not ai_response or len(ai_response) < 10 or 
                ai_response.count(ai_response[:20]) > 1 or _looks_low_quality(ai_response)):
                # GPT-2 response is poor, use template instead
                ai_response = ""
            
        except Exception as e:
            print(f"Error generating GPT-2 response: {e}")
            ai_response = ""
        
        # Handle crisis detection with appropriate response
        if crisis_detected:
            ai_response = (
                "I'm really glad you told me. I'm worried about your safety. Your life matters. "
                "Please reach out for help right now:\n\n"
                "Crisis resources:\n"
                "- In the US: Call or text 988 (Lifeline).\n"
                "- Text HOME to 741741 (Crisis Text Line).\n"
                "- Call local emergency services (e.g., 911) if you're in immediate danger.\n\n"
                "If you're outside the US, contact your local emergency number or visit findahelpline.com to find support in your country. "
                "If you can, consider reaching out to a trusted person nearby to stay with you."
            )
        # Use template-based responses if GPT-2 failed or generated poor response
        elif not ai_response:
            # Empathetic fallback generator
            def empathetic_fallback(e: str, user_text: str) -> str:
                t = (user_text or "").strip()
                if len(t) > 180:
                    t = t[:180].rstrip() + "..."
                q = t.lower()
                # Actionable follow-ups for direct help requests
                if any(phrase in q for phrase in ["what should i do", "what do i do", "how can i", "help me", "what next"]):
                    if e in ["sadness", "fear", "anger", "disgust", "surprise", "neutral"]:
                        return (
                            "Thank you for asking. One small step now could help: would it feel okay to write down what happened,"
                            " or message someone you trust, or take a short walk to settle your body? Which of these feels most doable?"
                        )
                # If user says we didn't answer, return to last user point
                if any(phrase in q for phrase in ["you didn't answer", "you did not answer", "answer the previous", "you didnt answer"]):
                    ref = (last_user_text or "that last point").strip()
                    if len(ref) > 120:
                        ref = ref[:120].rstrip() + "..."
                    return f"You're right—let me come back to what you shared about '{ref}'. What part of that feels heaviest right now?"
                # Targeted compassion for self-worth themes
                if any(phrase in q for phrase in ["not good enough", "i'm not enough", "im not enough", "i am not enough"]):
                    return "Hearing that makes sense after being insulted. Your worth isn’t defined by others’ judgments. What did that comment touch in you?"
                if e == 'sadness':
                    return f"That sounds really hard. It makes sense you'd feel sad about that. What would feel most supportive right now?"
                if e == 'fear':
                    return "Feeling scared can be exhausting. What part of this feels most worrying for you?"
                if e == 'anger':
                    return "I hear the anger there—your reaction is understandable. What happened that hurt the most?"
                if e == 'disgust':
                    return "That reaction makes sense given what you described. What about it feels most upsetting?"
                if e == 'surprise':
                    return "That sounds unexpected. What surprised you the most about it?"
                if e == 'joy':
                    return "I'm glad there's a bit of light here. What about this is bringing you joy?"
                return "I'm here with you. What feels most important to share next?"

            ai_response = empathetic_fallback(emotion, user_message)
        
        # Prepare emotion data for database storage
        emotion_data = {
            'emotion': emotion,
            'severity': 'high' if crisis_detected else 'low',
            'confidence': 0.8
        }
        
        # Save context to PostgreSQL via LangChain memory
        memory.save_context(
            inputs={'user_message': user_message},
            outputs={
                'response': ai_response,
                'emotion': emotion,
                'severity': emotion_data['severity'],
                'confidence': emotion_data['confidence']
            }
        )
        
        return ChatResponse(
            response=ai_response,
            emotion=emotion,
            severity=emotion_data['severity'],
            crisis_detected=crisis_detected,
            session_id=session_id
        )

    # --- Get conversation history for a session ---
    def get_conversation_history(self, session_id: str, user_id: str) -> list:
        """Get conversation history for a specific session"""
        memory = PostgresConversationMemory(
            session_id=session_id,
            user_id=user_id,
            max_messages=50  # Get more messages for history
        )
        
        messages = []
        for msg in memory.chat_memory._messages:
            if isinstance(msg, HumanMessage):
                messages.append({
                    'sender': 'user',
                    'message': msg.content,
                    'timestamp': datetime.now().isoformat()  # Approximate timestamp
                })
            elif isinstance(msg, AIMessage):
                messages.append({
                    'sender': 'ai',
                    'message': msg.content,
                    'timestamp': datetime.now().isoformat()  # Approximate timestamp
                })
        
        return messages

    # --- Get session information ---
    def get_session_info(self, session_id: str, user_id: str) -> dict:
        """Get detailed session information"""
        memory = PostgresConversationMemory(
            session_id=session_id,
            user_id=user_id
        )
        return memory.get_session_info()


# --- Global chatbot instance ---
chatbot = EmotionAwareChatbot()

def get_chatbot():
    return chatbot
