import { createAuthClient } from "better-auth/react";
import { useState, useEffect } from "react";

export const authClient = createAuthClient();

export const useSession = () => {
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const sessionData = await authClient.getSession();
        setSession(sessionData);
      } catch (error) {
        setSession(null);
      } finally {
        setLoading(false);
      }
    };

    checkSession();
  }, []);

  return { session, loading };
};