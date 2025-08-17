import { useState } from "react";

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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
          session_id: "session-" + Date.now()
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
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
      sadness: '#3b82f6', 
      anger: '#ef4444',
      fear: '#8b5cf6',
      surprise: '#f59e0b',
      disgust: '#84cc16',
      neutral: '#6b7280',
      crisis: '#dc2626'
    };
    return colors[emotion] || '#6b7280';
  };

  const getSeverityText = (severity) => {
    if (severity <= 3) return "Low";
    if (severity <= 6) return "Medium";
    if (severity <= 8) return "High";
    return "Critical";
  };

  return (
    <div style={{ maxWidth: 800, margin: "20px auto", fontFamily: "Inter, sans-serif", padding: "0 20px" }}>
      <div style={{ textAlign: "center", marginBottom: 30 }}>
        <h1 style={{ color: "#1f2937", marginBottom: 10 }}>🤗 FeelMate Chat</h1>
        <p style={{ color: "#6b7280", fontSize: "16px" }}>Share your feelings anonymously and get emotional support</p>
      </div>

      {/* Chat Messages */}
      <div style={{ 
        border: "1px solid #e5e7eb", 
        borderRadius: 12, 
        padding: 20, 
        minHeight: 400,
        maxHeight: 500,
        overflowY: "auto",
        backgroundColor: "#fafafa"
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
                backgroundColor: m.from === "user" ? "#4f46e5" : "white",
                color: m.from === "user" ? "white" : "#1f2937",
                border: m.from === "user" ? "none" : "1px solid #e5e7eb",
                boxShadow: m.from === "user" ? "none" : "0 1px 3px rgba(0,0,0,0.1)"
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
                  <div style={{ marginTop: 12, padding: "8px 12px", backgroundColor: "#fef3c7", borderRadius: 8 }}>
                    <div style={{ fontSize: "12px", fontWeight: "bold", color: "#92400e", marginBottom: 4 }}>
                      💡 Resources that might help:
                    </div>
                    {m.resources.map((resource, idx) => (
                      <div key={idx} style={{ fontSize: "11px", marginTop: 2 }}>
                        <a 
                          href={resource.url || "#"} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          style={{ color: "#92400e", textDecoration: "underline" }}
                        >
                          {resource.name}
                        </a>
                        {resource.description && (
                          <span style={{ color: "#92400e", marginLeft: 4 }}>
                            - {resource.description}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <div style={{ 
                  fontSize: "10px", 
                  color: m.from === "user" ? "rgba(255,255,255,0.7)" : "#9ca3af",
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
      <div style={{ display: "flex", marginTop: 20, gap: 10 }}>
        <input 
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Share how you're feeling..."
          disabled={isLoading}
          style={{ 
            flex: 1, 
            padding: "12px 16px", 
            borderRadius: 25, 
            border: "1px solid #e5e7eb",
            fontSize: "16px",
            outline: "none",
            transition: "border-color 0.2s",
            backgroundColor: isLoading ? "#f3f4f6" : "white"
          }}
        />
        <button 
          onClick={sendMessage} 
          disabled={isLoading || !input.trim()}
          style={{ 
            padding: "12px 24px", 
            borderRadius: 25, 
            border: "none", 
            backgroundColor: isLoading || !input.trim() ? "#9ca3af" : "#4f46e5", 
            color: "white",
            fontSize: "16px",
            fontWeight: "500",
            cursor: isLoading || !input.trim() ? "not-allowed" : "pointer",
            transition: "background-color 0.2s"
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
