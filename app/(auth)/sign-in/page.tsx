"use client";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await authClient.signIn.email({
        email,
        password,
        rememberMe: true,
        callbackURL: "",
      });
      router.push("/chat");
    } catch (err: any) {
      setError(err.message || "Sign in failed");
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color: "white",
        fontFamily: "Inter, sans-serif",
        padding: 20,
      }}
    >
      <h1 style={{ fontSize: 40, marginBottom: 20 }}>Sign In</h1>
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 16,
          minWidth: 320,
          background: "rgba(0,0,0,0.2)",
          padding: 32,
          borderRadius: 16,
        }}
      >
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          style={{
            padding: "12px",
            borderRadius: 8,
            border: "none",
            fontSize: 18,
          }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          style={{
            padding: "12px",
            borderRadius: 8,
            border: "none",
            fontSize: 18,
          }}
        />
        <button
          type="submit"
          style={{
            padding: "12px",
            borderRadius: 8,
            border: "none",
            backgroundColor: "#f6e05e",
            color: "#333",
            fontWeight: "bold",
            fontSize: 18,
            cursor: "pointer",
            transition: "0.3s",
          }}
        >
          Sign In
        </button>
        {error && (
          <div style={{ color: "#ff6b6b", marginTop: 8, textAlign: "center" }}>
            {error}
          </div>
        )}
      </form>
      <p style={{ marginTop: 24, fontSize: 16 }}>
        Don't have an account?{" "}
        <span
          style={{
            color: "#f6e05e",
            cursor: "pointer",
            textDecoration: "underline",
            fontWeight: "bold",
          }}
          onClick={() => router.push("/sign-up")}
        >
          Sign Up
        </span>
      </p>
    </div>
  );
}