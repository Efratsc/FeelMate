"use client";
import { useState } from "react";
import ChatBox from "../../components/ChatBox";
import AuthGuard from "../../components/AuthGuard";
import UserProfile from "../../components/UserProfile";

export default function ChatPage() {
  const [showSidebar, setShowSidebar] = useState(false);
  return (
    <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 20px" }}>
      <div
        style={{
          marginBottom: 16,
          padding: "12px 16px",
          borderRadius: 12,
          background: "rgba(255,255,255,0.7)",
          border: "1px solid rgba(0,0,0,0.06)",
          color: "#374151",
          display: "flex",
          alignItems: "center",
          gap: 10
        }}
      >
        <span style={{ fontSize: 18 }}>🫶</span>
        <span style={{ fontSize: 14 }}>
          This is a safe, supportive space. You can share as much or as little as you want.
        </span>
      </div>
      <AuthGuard>
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
                  border: "1px solid var(--border)",
                  background: "var(--card)",
                  color: "var(--text)",
                  cursor: "pointer"
                }}
              >
                {showSidebar ? "Hide Panel" : "Show Panel"}
              </button>
            </div>
            <ChatBox />
          </div>
        </div>
      </AuthGuard>
    </div>
  );
}