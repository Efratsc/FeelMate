import { useState } from "react";

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = input.trim();
    setInput("");
    setIsLoading(true);
    
    // Add user message immediately
    setMessages(prev => [...prev, { 
      text: userMessage, 
      from: "user",
      timestamp: new Date().toLocaleTimeString()
    }]);

    try {
      const response = await fetch('http://localhost:8001/api/chat/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          user_id: "user-123", // You can get this from auth context
          session_id: sessionId // Use existing session or null for new session
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      // Store session ID for future messages
      if (!sessionId) {
        setSessionId(data.session_id);
      }
      
      // Add AI response with emotion data
      setMessages(prev => [...prev, { 
        text: data.response,
        from: "ai",
        emotion: data.emotion,
        severity: data.severity,
        confidence: data.confidence,
        needs_help: data.needs_help,
        resources: data.resources,
        timestamp: new Date().toLocaleTimeString()
      }]);

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        text: "I'm sorry, I'm having trouble connecting right now. Please try again.",
        from: "ai",
        error: true,
        timestamp: new Date().toLocaleTimeString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getEmotionColor = (emotion) => {
    const colors = {
      joy: '#10b981',
      happy: '#10b981',
      sad: '#3b82f6',
      sadness: '#3b82f6',
      angry: '#ef4444',
      anger: '#ef4444',
      anxious: '#8b5cf6',
      fear: '#8b5cf6',
      confused: '#f59e0b',
      neutral: '#6b7280',
      crisis: '#dc2626'
    };
    return colors[emotion] || '#6b7280';
  };

  const getSeverityText = (severity) => {
    // Handle string severity values from backend
    if (typeof severity === 'string') {
      return severity.charAt(0).toUpperCase() + severity.slice(1);
    }
    
    // Fallback for numeric values (if any)
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
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          background: "var(--card)",
          border: "1px solid var(--border)",
          borderRadius: 14,
          padding: "14px 16px",
          marginBottom: 14
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 40, height: 40, borderRadius: 12, background: "linear-gradient(135deg,#6366f1,#8b5cf6)", display: "grid", placeItems: "center", color: "#fff", fontSize: 18 }}>💜</div>
          <div>
            <div style={{ fontWeight: 700, color: "var(--text)" }}>FeelMate</div>
            <div style={{ fontSize: 12, color: "#059669" }}>online • here to listen</div>
          </div>
        </div>
        <div style={{ fontSize: 12, color: "var(--muted)" }}>Your messages are not shared. This is a judgment‑free space.</div>
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
        {messages.length === 0 && (
          <div style={{ textAlign: "center", color: "#9ca3af", marginTop: 100 }}>
            <p>👋 Hi! I'm here to listen and support you.</p>
            <p>Share how you're feeling today...</p>
          </div>
        )}
        
        {messages.map((m, i) => (
          <div key={i} style={{ margin: "15px 0" }}>
            <div style={{ 
              display: "flex", 
              justifyContent: m.from === "user" ? "flex-end" : "flex-start",
              marginBottom: 5
            }}>
              <div style={{ 
                maxWidth: "70%",
                padding: "12px 16px",
                borderRadius: m.from === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                backgroundColor: m.from === "user" ? "#4f46e5" : "var(--ai-bubble)",
                color: m.from === "user" ? "white" : "var(--text)",
                border: m.from === "user" ? "none" : "1px solid var(--border)",
                boxShadow: m.from === "user" ? "none" : "0 1px 3px rgba(0,0,0,0.06)"
              }}>
                <div>{m.text}</div>
                
                {/* Emotion indicator for AI messages */}
                {m.from === "ai" && m.emotion && (
                  <div style={{ 
                    marginTop: 8, 
                    fontSize: "12px", 
                    display: "flex", 
                    alignItems: "center", 
                    gap: 8 
                  }}>
                    <span style={{ 
                      backgroundColor: getEmotionColor(m.emotion),
                      color: "white",
                      padding: "2px 8px",
                      borderRadius: 12,
                      fontSize: "10px",
                      textTransform: "uppercase",
                      fontWeight: "bold"
                    }}>
                      {m.emotion}
                    </span>
                    {m.severity && (
                      <span style={{ color: "#6b7280" }}>
                        Severity: {getSeverityText(m.severity)}
                      </span>
                    )}
                  </div>
                )}

                {/* Resources for high severity */}
                {m.from === "ai" && m.needs_help && m.resources && m.resources.length > 0 && (
                  <div style={{ marginTop: 12, padding: "8px 12px", backgroundColor: "var(--chip)", borderRadius: 8 }}>
                    <div style={{ fontSize: "12px", fontWeight: "bold", color: "#a78bfa", marginBottom: 4 }}>
                      💡 Resources that might help:
                    </div>
                    {m.resources.map((resource, idx) => (
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
                  color: m.from === "user" ? "rgba(255,255,255,0.7)" : "var(--muted)",
                  marginTop: 4,
                  textAlign: "right"
                }}>
                  {m.timestamp}
                </div>
              </div>
            </div>
          </div>
        ))}

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
      <div style={{ display: "flex", marginTop: 14, gap: 10 }}>
        <input 
          value={input}
          onChange={e => setInput(e.target.value)}
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
          onClick={sendMessage} 
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
      </div>

      <style jsx>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }
      `}</style>
    </div>
  );
}
