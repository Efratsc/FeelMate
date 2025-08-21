"use client";
import { useSession } from "../lib/auth-client";
import ChatBox from "../../components/ChatBox";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function ChatPage() {
  const { data, isPending } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!isPending && !data) {
      router.push("/sign-in");
    }
  }, [data, isPending, router]);

  if (isPending) return <p style={{ textAlign: "center", padding: 24 }}>Loading...</p>;
  if (!data) return null; // waiting for redirect

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 20px" }}>
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
        <span style={{ fontSize: 14 }}>This is a safe, supportive space. You can share as much or as little as you want.</span>
      </div>
      <ChatBox />
    </div>
  );
}
