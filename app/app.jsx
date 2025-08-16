import { useSession } from "./auth/auth-client";
import ChatBox from "../components/ChatBox";
import { useRouter } from "next/router";
import { useEffect } from "react";

export default function ChatPage() {
  const { session, isLoading } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !session) {
      router.push("/auth");
    }
  }, [session, isLoading, router]);

  if (isLoading) return <p>Loading...</p>;
  if (!session) return null; // waiting for redirect

  return <ChatBox />;
}
