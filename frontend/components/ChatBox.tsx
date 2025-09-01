'use client';
import { useState } from "react";

// Define a type for message metadata
interface MessageMetadata {
  emotion?: string;
  severity?: string | number;
  confidence?: number;
  needs_help?: boolean;
  resources?: Array<{ name: string; url?: string; description?: string }>;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: MessageMetadata;
}

export default function ChatBox() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          user_id: "demo-user-id",
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Check for session ID in headers
      const newSessionId = response.headers.get('X-Session-ID');
      if (newSessionId && !sessionId) {
        setSessionId(newSessionId);
      }

      // Create an assistant message and stream in characters for a typewriter effect
      const assistantId = (Date.now() + 1).toString();
      const fullText: string = data.response || '';

      // Seed empty assistant message
      setMessages(prev => [
        ...prev,
        {
          id: assistantId,
          role: 'assistant',
          content: '',
          metadata: {
            emotion: data.emotion,
            severity: data.severity,
            confidence: data.confidence,
            needs_help: data.needs_help,
            resources: data.resources,
          }
        }
      ]);

      // Typewriter animation
      const stepDelayMs = Math.min(40, Math.max(15, Math.floor(1200 / Math.max(10, fullText.length))));
      for (let i = 0; i < fullText.length; i++) {
        await new Promise(res => setTimeout(res, stepDelayMs));
        const slice = fullText.slice(0, i + 1);
        setMessages(prev => prev.map(m => m.id === assistantId ? { ...m, content: slice } : m));
      }

      // Ensure metadata is set even if response is empty
      setMessages(prev => prev.map(m => m.id === assistantId ? {
        ...m,
        metadata: {
          emotion: data.emotion,
          severity: data.severity,
          confidence: data.confidence,
          needs_help: data.needs_help,
          resources: data.resources,
        }
      } : m));
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  // Helper function to get metadata from a message
  const getMessageMetadata = (message: any): MessageMetadata => {
    // Vercel AI SDK stores custom data in various places
    return {
      emotion: message.emotion || message?.additionalData?.emotion,
      severity: message.severity || message?.additionalData?.severity,
      confidence: message.confidence || message?.additionalData?.confidence,
      needs_help: message.needs_help || message?.additionalData?.needs_help,
      resources: message.resources || message?.additionalData?.resources,
    };
  };

  const getEmotionColor = (emotion: string) => {
    const colors: Record<string, string> = {
      joy: '#10b981', happy: '#10b981',
      sad: '#3b82f6', sadness: '#3b82f6',
      angry: '#ef4444', anger: '#ef4444',
      anxious: '#8b5cf6', fear: '#8b5cf6',
      confused: '#f59e0b', neutral: '#6b7280',
      crisis: '#dc2626'
    };
    return colors[emotion] || '#6b7280';
  };

  const getSeverityText = (severity: any) => {
    if (typeof severity === 'string') {
      return severity.charAt(0).toUpperCase() + severity.slice(1);
    }
    if (typeof severity === 'number') {
      if (severity <= 3) return "Low";
      if (severity <= 6) return "Medium";
      if (severity <= 8) return "High";
      return "Critical";
    }
    return "Unknown";
  };

  return (
    <div style={{ maxWidth: 900, margin: "20px auto", fontFamily: "Inter, sans-serif", padding: "0 20px" }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 30 }}>
        <h1 style={{ 
          fontSize: "2.5rem", 
          fontWeight: 700, 
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          marginBottom: 10
        }}>
          FeelMate
        </h1>
        <p style={{ 
          fontSize: "1.1rem", 
          color: "#6b7280", 
          maxWidth: 500, 
          margin: "0 auto",
          lineHeight: 1.6
        }}>
          Your AI companion for emotional support and mental wellness
        </p>
      </div>
      
      {/* Chat Messages */}
      <div style={{ 
        border: "1px solid var(--border)", 
        borderRadius: 16, 
        padding: 20, 
        minHeight: 440,
        maxHeight: 560,
        overflowY: "auto",
        backgroundColor: "var(--card-solid)",
        boxShadow: "0 10px 30px rgba(99,102,241,0.05)"
      }}>
        {messages.map((m) => {
          const metadata = getMessageMetadata(m);
          
          return (
            <div key={m.id} style={{ margin: "15px 0" }}>
              <div style={{ 
                display: "flex", 
                justifyContent: m.role === 'user' ? "flex-end" : "flex-start",
                marginBottom: 5
              }}>
                <div style={{ 
                  maxWidth: "70%",
                  padding: "12px 16px",
                  borderRadius: m.role === 'user' ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                  backgroundColor: m.role === 'user' ? "#4f46e5" : "var(--ai-bubble)",
                  color: m.role === 'user' ? "white" : "var(--text)",
                  border: m.role === 'user' ? "none" : "1px solid var(--border)",
                  boxShadow: m.role === 'user' ? "none" : "0 1px 3px rgba(0,0,0,0.06)"
                }}>
                  <div>{m.content}</div>
                  
                  {/* Emotion indicator */}
                  {m.role === 'assistant' && metadata.emotion && (
                    <div style={{ 
                      marginTop: 8, 
                      fontSize: "12px", 
                      display: "flex", 
                      alignItems: "center", 
                      gap: 8 
                    }}>
                      <span style={{ 
                        backgroundColor: getEmotionColor(metadata.emotion),
                        color: "white",
                        padding: "2px 8px",
                        borderRadius: 12,
                        fontSize: "10px",
                        textTransform: "uppercase",
                        fontWeight: "bold"
                      }}>
                        {metadata.emotion}
                      </span>
                      {metadata.severity && (
                        <span style={{ color: "#6b7280" }}>
                          Severity: {getSeverityText(metadata.severity)}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Resources section */}
                  {m.role === 'assistant' && metadata.needs_help && metadata.resources && metadata.resources.length > 0 && (
                    <div style={{ marginTop: 12, padding: "8px 12px", backgroundColor: "var(--chip)", borderRadius: 8 }}>
                      <div style={{ fontSize: "12px", fontWeight: "bold", color: "#a78bfa", marginBottom: 4 }}>
                        💡 Resources that might help:
                      </div>
                      {metadata.resources.map((resource, idx) => (
                        <div key={idx} style={{ fontSize: "11px", marginTop: 2 }}>
                          <a 
                            href={resource.url || "#"} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            style={{ color: "#a78bfa", textDecoration: "underline" }}
                          >
                            {resource.name}
                          </a>
                          {resource.description && (
                            <span style={{ color: "#a78bfa", marginLeft: 4 }}>
                              - {resource.description}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  <div style={{ 
                    fontSize: "10px", 
                    color: m.role === 'user' ? "rgba(255,255,255,0.7)" : "var(--muted)",
                    marginTop: 4,
                    textAlign: "right"
                  }}>
                    {new Date().toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
        
         {/* Loading indicator */}
        {isLoading && (
          <div style={{ display: "flex", justifyContent: "flex-start", margin: "15px 0" }}>
            <div style={{ 
              padding: "12px 16px",
              borderRadius: "18px 18px 18px 4px",
              backgroundColor: "white",
              border: "1px solid #e5e7eb",
              display: "flex",
              alignItems: "center",
              gap: 8
            }}>
              <div style={{ display: "flex", gap: 4 }}>
                <div style={{ width: 8, height: 8, backgroundColor: "#4f46e5", borderRadius: "50%", animation: "bounce 1.4s infinite ease-in-out" }}></div>
                <div style={{ width: 8, height: 8, backgroundColor: "#4f46e5", borderRadius: "50%", animation: "bounce 1.4s infinite ease-in-out 0.2s" }}></div>
                <div style={{ width: 8, height: 8, backgroundColor: "#4f46e5", borderRadius: "50%", animation: "bounce 1.4s infinite ease-in-out 0.4s" }}></div>
              </div>
              <span style={{ fontSize: "12px", color: "#6b7280" }}>Thinking...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} style={{ display: "flex", marginTop: 14, gap: 10 }}>
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Share how you're feeling..."
          disabled={isLoading}
          style={{ 
            flex: 1,
            padding: "12px 16px",
            borderRadius: 14,
            border: "1px solid var(--border)",
            fontSize: "16px",
            outline: "none",
            transition: "border-color 0.2s",
            backgroundColor: isLoading ? "#f3f4f6" : "var(--card-solid)",
            boxShadow: "0 2px 8px rgba(0,0,0,0.04)"
          }}
        />
        <button 
          type="submit"
          disabled={isLoading || !input.trim()}
          style={{ 
            padding: "12px 20px",
            borderRadius: 12,
            border: "1px solid var(--brand)",
            backgroundColor: isLoading || !input.trim() ? "#9ca3af" : "var(--brand)",
            color: "white",
            fontSize: "15px",
            fontWeight: 600,
            cursor: isLoading || !input.trim() ? "not-allowed" : "pointer",
            transition: "background-color 0.2s, transform 0.05s"
          }}
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>

      <style jsx>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }
      `}</style>
    </div>
  );
}