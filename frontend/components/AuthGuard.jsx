import { useSession } from "../app/lib/auth-client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function AuthGuard({ children, requireAuth = true }) {
  const { session, isLoading } = useSession();
  const router = useRouter();
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);

  useEffect(() => {
    // Only redirect after we've checked authentication and confirmed user is not authenticated
    if (!isLoading && !hasCheckedAuth) {
      setHasCheckedAuth(true);
      
      if (requireAuth && !session) {
        console.log("AuthGuard: User not authenticated, redirecting to sign-in");
        router.push('/sign-in');
      } else if (requireAuth && session) {
        console.log("AuthGuard: User authenticated, allowing access");
      }
    }
  }, [session, isLoading, requireAuth, router, hasCheckedAuth]);

  // Show loading state while checking authentication
  if (isLoading || (!hasCheckedAuth && requireAuth)) {
    return (
      <div style={{ 
        display: "flex", 
        justifyContent: "center", 
        alignItems: "center", 
        minHeight: "100vh",
        fontFamily: "Inter, sans-serif"
      }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "18px", color: "var(--text)", marginBottom: "8px" }}>
            Loading...
          </div>
          <div style={{ fontSize: "14px", color: "var(--muted)" }}>
            Checking authentication
          </div>
        </div>
      </div>
    );
  }

  // If auth is required and user is not authenticated, don't render children
  if (requireAuth && !session && hasCheckedAuth) {
    return null;
  }

  // Render children if authenticated or auth not required
  return children;
}
