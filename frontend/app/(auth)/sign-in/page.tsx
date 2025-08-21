"use client";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    
    try {
      const result = await authClient.signIn.email({
        email,
        password,
        callbackURL: "/chat",
      });
      
      // If we reach here, authentication was successful
      // The authClient will handle the redirect automatically
      console.log("Sign in successful:", result);
      
    } catch (err: any) {
      console.error("Sign in error:", err);
      setError(err.message || "Sign in failed. Please check your email and password.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: "grid", placeItems: "center", minHeight: "calc(100vh - 120px)", padding: 24 }}>
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 16,
          width: "100%",
          maxWidth: 400,
          background: "rgba(255,255,255,0.8)",
          backdropFilter: "saturate(180%) blur(10px)",
          padding: 28,
          borderRadius: 16,
          border: "1px solid rgba(0,0,0,0.06)",
          boxShadow: "0 10px 30px rgba(99,102,241,0.08)",
          color: "#111827"
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 4 }}>
          <div style={{ fontSize: 28 }}>💜</div>
          <h1 style={{ fontSize: 24, margin: "8px 0 2px" }}>Welcome back</h1>
          <p style={{ margin: 0, color: "#6b7280", fontSize: 13 }}>You are safe here. Your privacy matters.</p>
        </div>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          disabled={isLoading}
          style={{
            padding: "12px",
            borderRadius: 8,
            border: "1px solid #e5e7eb",
            fontSize: 16,
            opacity: isLoading ? 0.7 : 1,
          }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          disabled={isLoading}
          style={{
            padding: "12px",
            borderRadius: 8,
            border: "1px solid #e5e7eb",
            fontSize: 16,
            opacity: isLoading ? 0.7 : 1,
          }}
        />
        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: "12px",
            borderRadius: 8,
            border: "1px solid #111827",
            backgroundColor: isLoading ? "#9ca3af" : "#111827",
            color: "#fff",
            fontWeight: 600,
            fontSize: 16,
            cursor: isLoading ? "not-allowed" : "pointer",
            transition: "0.3s",
          }}
        >
          {isLoading ? "Signing In..." : "Sign In"}
        </button>
        {error && (
          <div style={{ color: "#b91c1c", marginTop: 8, textAlign: "center", fontSize: 13 }}>
            {error}
          </div>
        )}
        <p style={{ marginTop: 6, fontSize: 13, textAlign: "center", color: "#6b7280" }}>
          Don't have an account?{" "}
          <span
            style={{ color: "#111827", cursor: "pointer", textDecoration: "underline", fontWeight: 600 }}
            onClick={() => router.push("/sign-up")}
          >
            Sign Up
          </span>
        </p>
      </form>
    </div>
  );
}