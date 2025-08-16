import { signIn, signUp, useSession } from "../app/auth/auth-client";
import { useRouter } from "next/router";
import { useEffect } from "react";

export default function AuthPage() {
  const router = useRouter();
  const { session, isLoading } = useSession();

  // Redirect to /app if already logged in
  useEffect(() => {
    if (session) {
      router.push("/app");
    }
  }, [session, router]);

  if (isLoading) return <p>Loading...</p>;

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      color: "white",
      fontFamily: "Inter, sans-serif",
      textAlign: "center",
      padding: 20
    }}>
      <h1 style={{ fontSize: 48, marginBottom: 20 }}>FeelMate</h1>
      <p style={{ fontSize: 20, marginBottom: 40 }}>
        Please sign in or sign up to continue
      </p>
      <div style={{ display: "flex", gap: 20 }}>
        <button
          onClick={() => signIn({ redirectTo: "/app" })}
          style={{
            padding: "12px 28px",
            fontSize: "16px",
            borderRadius: "8px",
            border: "none",
            backgroundColor: "#f6e05e",
            color: "#333",
            fontWeight: "bold",
            cursor: "pointer",
            transition: "0.3s",
          }}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#ecc94b")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "#f6e05e")}
        >
          Sign In
        </button>

        <button
          onClick={() => signUp({ redirectTo: "/app" })}
          style={{
            padding: "12px 28px",
            fontSize: "16px",
            borderRadius: "8px",
            border: "none",
            backgroundColor: "#48bb78",
            color: "white",
            fontWeight: "bold",
            cursor: "pointer",
            transition: "0.3s",
          }}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#38a169")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "#48bb78")}
        >
          Sign Up
        </button>
      </div>
    </div>
  );
}
