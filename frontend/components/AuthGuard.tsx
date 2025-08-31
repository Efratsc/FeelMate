"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/lib/auth-client";

/**
 * @param {Object} props
 * @param {React.ReactNode} props.children
 */
export default function AuthGuard({ children }) {
  const router = useRouter();
  const { session, loading } = useSession();

  useEffect(() => {
    if (!loading && !session) {
      router.push("/sign-in");
    }
  }, [session, loading, router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return session ? <>{children}</> : null;
}