"use client";
import { useRouter } from "next/navigation";
import React from "react";

export default function Landing() {
  const router = useRouter();

  return (
    <div>
      {/* Landing-only header */}
      <div
        style={{
          position: "sticky",
          top: 0,
          zIndex: 10,
          background: "rgba(255,255,255,0.7)",
          backdropFilter: "saturate(180%) blur(8px)",
          borderBottom: "1px solid rgba(0,0,0,0.06)",
        }}
      >
        <div
          style={{
            maxWidth: 1100,
            margin: "0 auto",
            padding: "14px 20px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              display: "grid", placeItems: "center", color: "white", fontWeight: 800
            }}>💜</div>
            <span style={{ fontWeight: 800, color: "#111827", letterSpacing: 0.2 }}>FeelMate</span>
          </div>
          <nav style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <a href="/chat" style={{ color: "#374151", textDecoration: "none" }}>Chat</a>
            <a href="/sign-in" style={{ color: "#374151", textDecoration: "none" }}>Sign in</a>
            <a
              href="/sign-up"
              style={{
                textDecoration: "none",
                background: "#111827",
                color: "#fff",
                padding: "8px 14px",
                borderRadius: 10,
                fontWeight: 600,
              }}
            >
              Create account
            </a>
          </nav>
        </div>
      </div>

      <div style={{ display: "grid", placeItems: "center", minHeight: "calc(100vh - 120px)", padding: 24 }}>
      <section
        style={{
          width: "100%",
          maxWidth: 980,
          margin: "0 auto",
          padding: 28,
          borderRadius: 24,
          background: "rgba(255,255,255,0.7)",
          backdropFilter: "saturate(180%) blur(10px)",
          border: "1px solid rgba(0,0,0,0.06)",
          boxShadow: "0 10px 30px rgba(99,102,241,0.08)",
          textAlign: "center",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 16, alignItems: "center" }}>
          <div style={{ fontSize: 50 }}>💜</div>
          <h1 style={{ fontSize: 44, margin: 0, letterSpacing: -0.5 }}>FeelMate</h1>
          <p style={{ fontSize: 18, color: "#4b5563", maxWidth: 700, margin: 0 }}>
            A calm, welcoming space to share how you feel. FeelMate listens without judgment and responds with empathy
            and gentle guidance. You are not alone here.
          </p>
          <div style={{ display: "flex", gap: 12, marginTop: 18, flexWrap: "wrap", justifyContent: "center" }}>
            <button
              onClick={() => router.push("/chat")}
              style={{
                padding: "12px 22px",
                borderRadius: 12,
                border: "1px solid #111827",
                background: "#111827",
                color: "#fff",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              Start chatting
            </button>
            <button
              onClick={() => router.push("/sign-up")}
              style={{
                padding: "12px 22px",
                borderRadius: 12,
                border: "1px solid rgba(0,0,0,0.12)",
                background: "#fff",
                color: "#111827",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              Create an account
            </button>
          </div>
          <div
            style={{
              marginTop: 18,
              display: "flex",
              gap: 12,
              flexWrap: "wrap",
              justifyContent: "center",
              color: "#6b7280",
              fontSize: 14
            }}
          >
            <span>Private by default</span>
            <span>•</span>
            <span>Non‑judgmental support</span>
            <span>•</span>
            <span>Available 24/7</span>
          </div>
        </div>
      </section>
      </div>
    </div>
  );
}