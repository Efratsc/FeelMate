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
      const metadata = {
        emotion: data.emotion,
        severity: data.severity,
        confidence: data.confidence,
        needs_help: data.needs_help,
        resources: data.resources,
      };
      

      
      setMessages(prev => prev.map(m => m.id === assistantId ? {
        ...m,
        metadata: metadata
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
    // Check our custom metadata structure first
    if (message.metadata) {
      return {
        emotion: message.metadata.emotion,
        severity: message.metadata.severity,
        confidence: message.metadata.confidence,
        needs_help: message.metadata.needs_help,
        resources: message.metadata.resources,
      };
    }
    
    // Fallback for Vercel AI SDK format
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
      surprised: '#f59e0b', disgusted: '#dc2626',
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
    <div style={{ 
      height: "100vh", 
      display: "flex", 
      flexDirection: "column", 
      fontFamily: "Inter, sans-serif",
      backgroundColor: "#f8fafc"
    }}>
      {/* Header */}
      <div style={{ 
        backgroundColor: "white", 
        borderBottom: "1px solid #e2e8f0", 
        padding: "16px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 40,
            height: 40,
            borderRadius: "50%",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontWeight: "bold",
            fontSize: "18px"
          }}>
            F
          </div>
          <div>
            <h1 style={{ 
              fontSize: "1.5rem", 
              fontWeight: 600, 
              margin: 0,
              color: "#1e293b"
            }}>
              FeelMate
            </h1>
            <p style={{ 
              fontSize: "0.875rem", 
              color: "#64748b", 
              margin: 0
            }}>
              Your AI companion for emotional support
            </p>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            backgroundColor: "#10b981"
          }}></div>
          <span style={{ fontSize: "0.875rem", color: "#64748b" }}>Online</span>
        </div>
      </div>
      
      {/* Chat Messages */}
      <div style={{ 
        flex: 1,
        overflowY: "auto",
        backgroundColor: "#f8fafc",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "16px"
      }}>
        {messages.map((m) => {
          const metadata = getMessageMetadata(m);
          

          
          return (
            <div key={m.id} style={{ 
              display: "flex", 
              justifyContent: m.role === 'user' ? "flex-end" : "flex-start",
              alignItems: "flex-start",
              gap: "12px"
            }}>
              {m.role === 'assistant' && (
                <div style={{
                  width: 32,
                  height: 32,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "white",
                  fontWeight: "bold",
                  fontSize: "14px",
                  flexShrink: 0
                }}>
                  F
                </div>
              )}
              
              <div style={{ 
                maxWidth: "70%",
                display: "flex",
                flexDirection: "column",
                gap: "8px"
              }}>
                <div style={{ 
                  padding: "16px 20px",
                  borderRadius: "20px",
                  backgroundColor: m.role === 'user' ? "#4f46e5" : "transparent",
                  color: m.role === 'user' ? "white" : "#1e293b",
                  border: m.role === 'user' ? "none" : "none",
                  boxShadow: m.role === 'user' ? "0 2px 8px rgba(79, 70, 229, 0.3)" : "none",
                  lineHeight: "1.6",
                  fontSize: "15px"
                }}>
                  {m.content}
                </div>
                  
                {/* Emotion indicator */}
                {m.role === 'assistant' && metadata.emotion && (
                  <div style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    gap: 12,
                    padding: "0 4px"
                  }}>
                    <span style={{ 
                      backgroundColor: getEmotionColor(metadata.emotion),
                      color: "white",
                      padding: "4px 12px",
                      borderRadius: 16,
                      fontSize: "11px",
                      textTransform: "uppercase",
                      fontWeight: "600",
                      letterSpacing: "0.5px"
                    }}>
                      {metadata.emotion}
                    </span>
                    {metadata.severity && (
                      <span style={{ 
                        color: "#64748b",
                        fontSize: "12px",
                        fontWeight: "500"
                      }}>
                        Severity: {getSeverityText(metadata.severity)}
                      </span>
                    )}
                  </div>
                )}

                {/* Resources section */}
                {m.role === 'assistant' && metadata.needs_help && metadata.resources && metadata.resources.length > 0 && (
                  <div style={{ 
                    padding: "16px 0", 
                    backgroundColor: "transparent", 
                    borderRadius: 0,
                    border: "none"
                  }}>
                    <div style={{ 
                      fontSize: "13px", 
                      fontWeight: "600", 
                      color: "#475569", 
                      marginBottom: 8,
                      display: "flex",
                      alignItems: "center",
                      gap: 6
                    }}>
                      💡 Resources that might help:
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      {metadata.resources.map((resource, idx) => (
                        <div key={idx} style={{ 
                          padding: "8px 0",
                          backgroundColor: "transparent",
                          borderRadius: 0,
                          border: "none"
                        }}>
                          <a 
                            href={resource.url || "#"} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            style={{ 
                              color: "#4f46e5", 
                              textDecoration: "none",
                              fontWeight: "500",
                              fontSize: "12px"
                            }}
                          >
                            {resource.name}
                          </a>
                          {resource.description && (
                            <div style={{ 
                              color: "#64748b", 
                              fontSize: "11px",
                              marginTop: 2
                            }}>
                              {resource.description}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            </div>
          );
        })}
        
        {/* Loading indicator */}
        {isLoading && (
          <div style={{ 
            display: "flex", 
            justifyContent: "flex-start", 
            alignItems: "flex-start",
            gap: "12px"
          }}>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontWeight: "bold",
              fontSize: "14px",
              flexShrink: 0
            }}>
              F
            </div>
            <div style={{ 
              padding: "16px 20px",
              borderRadius: "20px",
              backgroundColor: "transparent",
              border: "none",
              boxShadow: "none",
              display: "flex",
              alignItems: "center",
              gap: 12
            }}>
              <div style={{ display: "flex", gap: 4 }}>
                <div style={{ width: 6, height: 6, backgroundColor: "#4f46e5", borderRadius: "50%", animation: "bounce 1.4s infinite ease-in-out" }}></div>
                <div style={{ width: 6, height: 6, backgroundColor: "#4f46e5", borderRadius: "50%", animation: "bounce 1.4s infinite ease-in-out 0.2s" }}></div>
                <div style={{ width: 6, height: 6, backgroundColor: "#4f46e5", borderRadius: "50%", animation: "bounce 1.4s infinite ease-in-out 0.4s" }}></div>
              </div>
              <span style={{ fontSize: "14px", color: "#64748b", fontWeight: "500" }}>Thinking...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div style={{
        backgroundColor: "white",
        borderTop: "1px solid #e2e8f0",
        padding: "20px 24px"
      }}>
        <form onSubmit={handleSubmit} style={{ 
          display: "flex", 
          gap: 12,
          maxWidth: "800px",
          margin: "0 auto"
        }}>
          <div style={{ 
            flex: 1,
            position: "relative"
          }}>
            <input 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Share how you're feeling..."
              disabled={isLoading}
              style={{ 
                width: "100%",
                padding: "16px 20px",
                borderRadius: 24,
                border: "1px solid #e2e8f0",
                fontSize: "15px",
                outline: "none",
                transition: "all 0.2s",
                backgroundColor: isLoading ? "#f8fafc" : "white",
                boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                resize: "none"
              }}
            />
          </div>
          <button 
            type="submit"
            disabled={isLoading || !input.trim()}
            style={{ 
              padding: "16px 24px",
              borderRadius: 24,
              border: "none",
              backgroundColor: isLoading || !input.trim() ? "#cbd5e1" : "#4f46e5",
              color: "white",
              fontSize: "15px",
              fontWeight: 600,
              cursor: isLoading || !input.trim() ? "not-allowed" : "pointer",
              transition: "all 0.2s",
              boxShadow: isLoading || !input.trim() ? "none" : "0 2px 8px rgba(79, 70, 229, 0.3)",
              display: "flex",
              alignItems: "center",
              gap: 8
            }}
          >
            {isLoading ? (
              <>
                <div style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTop: "2px solid white", borderRadius: "50%", animation: "spin 1s linear infinite" }}></div>
                Sending...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22,2 15,22 11,13 2,9 22,2"></polygon>
                </svg>
                Send
              </>
            )}
          </button>
        </form>
      </div>

      <style jsx>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}