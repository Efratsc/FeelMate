"use client";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

export default function SignUpPage() {
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
      const result = await authClient.signUp.email({
        email: email,
        password: password,
        name: "anonymous",
        callbackURL: "/chat",
      });
      
      // If we reach here, user creation was successful
      // The authClient will handle the redirect automatically
      console.log("Sign up successful:", result);
      
    } catch (err: any) {
      console.error("Sign up error:", err);
      setError(err.message || "Sign up failed. Please try again.");
    } finally {
      setIsLoading(false);
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
      <h1 style={{ fontSize: 40, marginBottom: 20 }}>Sign Up</h1>
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
          disabled={isLoading}
          style={{
            padding: "12px",
            borderRadius: 8,
            border: "none",
            fontSize: 18,
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
            border: "none",
            fontSize: 18,
            opacity: isLoading ? 0.7 : 1,
          }}
        />
        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: "12px",
            borderRadius: 8,
            border: "none",
            backgroundColor: isLoading ? "#ccc" : "#f6e05e",
            color: "#333",
            fontWeight: "bold",
            fontSize: 18,
            cursor: isLoading ? "not-allowed" : "pointer",
            transition: "0.3s",
          }}
        >
          {isLoading ? "Creating Account..." : "Sign Up"}
        </button>
        {error && (
          <div style={{ color: "#ff6b6b", marginTop: 8, textAlign: "center" }}>
            {error}
          </div>
        )}
      </form>
      <p style={{ marginTop: 24, fontSize: 16 }}>
        Already have an account?{" "}
        <span
          style={{
            color: "#f6e05e",
            cursor: "pointer",
            textDecoration: "underline",
            fontWeight: "bold",
          }}
          onClick={() => router.push("/sign-in")}
        >
          Sign In
        </span>
      </p>
    </div>
  );
}