﻿"use client";
import { useState } from "react";
import ChatBox from "../../components/ChatBox";
import UserProfile from "../../components/UserProfile";

export default function ChatPage() {
  const [showSidebar, setShowSidebar] = useState(false);
  
  return (
    <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 20px" }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: showSidebar ? "300px 1fr" : "1fr",
          gap: 16,
          alignItems: "start"
        }}
      >
        {showSidebar && (
          <div style={{ position: "sticky", top: 20 }}>
            <UserProfile />
          </div>
        )}
        <div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 8
            }}
          >
            <div />
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              style={{
                padding: "8px 12px",
                borderRadius: 10,
                border: "1px solid #e5e7eb",
                background: "rgba(255,255,255,0.8)",
                color: "#111827",
                cursor: "pointer"
              }}
            >
              {showSidebar ? "Hide Panel" : "Show Panel"}
            </button>
          </div>
          <ChatBox />
        </div>
      </div>
    </div>
  );
}