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

  if (isPending) return <p>Loading...</p>;
  if (!data) return null; // waiting for redirect

  return <ChatBox />;
}
