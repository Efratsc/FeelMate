import { useState, useEffect } from "react";

export const useSession = () => {
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        // Use fetch directly instead of importing server-side modules
        const response = await fetch('/api/auth/get-session');
        if (response.ok) {
          const sessionData = await response.json();
          setSession(sessionData);
        } else {
          setSession(null);
        }
      } catch (error) {
        console.log("No session found:", error);
        setSession(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkSession();
  }, []);

  const signOut = async () => {
    try {
      await fetch('/api/auth/sign-out', { method: 'POST' });
      setSession(null);
    } catch (error) {
      console.error("Sign out error:", error);
    }
  };

  return { session, isLoading, signOut };
};

// Simple auth client for sign-in
export const authClient = {
  signIn: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);
    
    const response = await fetch('/api/auth/sign-in', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || "Sign in failed");
    }
    
    return response.json();
  },
  
  getSession: async () => {
    const response = await fetch('/api/auth/get-session');
    if (response.ok) {
      return response.json();
    }
    return null;
  }
};