import { useState } from "react";

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input) return;
    setMessages([...messages, { text: input, from: "user" }]);
    // Simulate AI response
    setMessages(prev => [...prev, { text: `AI: I hear you - "${input}"`, from: "ai" }]);
    setInput("");
  };

  return (
    <div style={{ maxWidth: 600, margin: "50px auto", fontFamily: "Inter, sans-serif" }}>
      <h2>FeelMate Chat</h2>
      <div style={{ border: "1px solid #ccc", borderRadius: 8, padding: 20, minHeight: 300 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ margin: "10px 0", textAlign: m.from === "user" ? "right" : "left" }}>
            <span style={{ background: m.from === "user" ? "#4f46e5" : "#f6e05e", color: m.from === "user" ? "white" : "#333", padding: "5px 10px", borderRadius: 5 }}>
              {m.text}
            </span>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", marginTop: 20 }}>
        <input 
          value={input}
          onChange={e => setInput(e.target.value)}
          style={{ flex: 1, padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
        />
        <button onClick={sendMessage} style={{ marginLeft: 10, padding: "10px 20px", borderRadius: 8, border: "none", backgroundColor: "#4f46e5", color: "white" }}>Send</button>
      </div>
    </div>
  );
}
