import { useState, useEffect } from "react";

// Shared session state to prevent multiple API calls
let sharedSession: any = null;
let sharedLoading = false;
let sessionListeners: ((session: any, loading: boolean) => void)[] = [];

const notifyListeners = () => {
  sessionListeners.forEach(listener => listener(sharedSession, sharedLoading));
};

const setSharedSession = (session: any) => {
  sharedSession = session;
  notifyListeners();
};

const setSharedLoading = (loading: boolean) => {
  sharedLoading = loading;
  notifyListeners();
};

// Global function to check session once
export const checkGlobalSession = async () => {
  if (sharedSession !== null) {
    console.log("Session already exists, returning:", sharedSession);
    return sharedSession; // Already checked
  }
  
  console.log("Checking global session...");
  setSharedLoading(true);
  try {
    const sessionData = await authClient.getSession();
    console.log("Global session check result:", sessionData);
    setSharedSession(sessionData);
    return sessionData;
  } catch (error) {
    console.log("No session found:", error);
    setSharedSession(null);
    return null;
  } finally {
    setSharedLoading(false);
  }
};

export const useSession = () => {
  const [session, setSession] = useState(sharedSession);
  const [isLoading, setIsLoading] = useState(sharedLoading);

  useEffect(() => {
    const listener = (newSession: any, newLoading: boolean) => {
      setSession(newSession);
      setIsLoading(newLoading);
    };
    
    sessionListeners.push(listener);
    
    // Only check session if not already done and not currently loading
    if (sharedSession === null && !sharedLoading) {
      checkGlobalSession();
    }
    
    return () => {
      const index = sessionListeners.indexOf(listener);
      if (index > -1) {
        sessionListeners.splice(index, 1);
      }
    };
  }, []);

  const checkSession = async () => {
    // Only check if we don't already have a session
    if (sharedSession === null) {
      return await checkGlobalSession();
    }
    return sharedSession;
  };

  const signOut = async () => {
    try {
      // Use the [...all] route for signout
      await fetch('/api/auth/[...all]', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'signout' })
      });
      setSharedSession(null);
    } catch (error) {
      console.error("Sign out error:", error);
    }
  };

  const updateSession = (newSession: any) => {
    console.log("Updating session:", newSession);
    setSharedSession(newSession);
  };

  const refreshSession = async () => {
    // Force a fresh session check from the server
    setSharedLoading(true);
    try {
      const sessionData = await authClient.getSession();
      console.log("Refreshed session:", sessionData);
      setSharedSession(sessionData);
      return sessionData;
    } catch (error) {
      console.log("Failed to refresh session:", error);
      setSharedSession(null);
      return null;
    } finally {
      setSharedLoading(false);
    }
  };

  return { session, isLoading, signOut, updateSession, refreshSession };
};

// Simple auth client for sign-in and sign-up
export const authClient = {
  // Backward-compatible, callable signIn with a nested .email method
  signIn: Object.assign(
    async (...args: any[]) => {
      // Support legacy usage: authClient.signIn(email, password [, rememberMe, callbackURL])
      if (typeof args[0] === 'string') {
        const [email, password, rememberMe, callbackURL] = args as [string, string, boolean?, string?];
        return await (authClient as any).signIn.email({ email, password, rememberMe, callbackURL });
      }
      // Or object usage: authClient.signIn({ email, password, ... })
      if (args[0] && typeof args[0] === 'object') {
        return await (authClient as any).signIn.email(args[0]);
      }
      throw new Error('Invalid arguments for signIn');
    },
    {
      email: async ({ email, password, rememberMe, callbackURL }: { 
        email: string; 
        password: string; 
        rememberMe?: boolean;
        callbackURL?: string;
      }) => {
        // Call Better Auth sign-in endpoint
        const response = await fetch('/api/auth/sign-in', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            email, 
            password,
            rememberMe,
            callbackURL
          })
        });
        
        if (!response.ok) {
          let errorMessage = "Sign in failed";
          try {
            const errorData = await response.json();
            errorMessage = errorData.message || errorMessage;
          } catch (e) {
            errorMessage = response.statusText || errorMessage;
          }
          throw new Error(errorMessage);
        }
        
        try {
          return await response.json();
        } catch (e) {
          return { success: true };
        }
      }
    }
  ),
  
  signUp: {
    email: async ({ email, password, name, image, callbackURL }: { 
      email: string; 
      password: string; 
      name: string; 
      image?: string;
      callbackURL?: string;
    }) => {
      // Call Better Auth sign-up endpoint
      const response = await fetch('/api/auth/sign-up', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email, 
          password, 
          name,
          image,
          callbackURL
        })
      });
      
      if (!response.ok) {
        let errorMessage = "Sign up failed";
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorMessage;
        } catch (e) {
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }
      
      try {
        return await response.json();
      } catch (e) {
        return { success: true };
      }
    }
  },
  
  getSession: async () => {
    // Probe multiple possible session endpoints with brief retries
    const endpoints = [
      '/api/auth/session',
      '/api/auth/me',
      '/api/auth/user',
      '/api/auth/[...all]'
    ];
    const tryEndpoint = async (url: string) => {
      try {
        const response = await fetch(url, { credentials: 'same-origin' });
        if (!response.ok) return null;
        return await response.json().catch(() => null);
      } catch {
        return null;
      }
    };
    for (const delayMs of [0, 150, 300, 600]) {
      if (delayMs) await new Promise(r => setTimeout(r, delayMs));
      for (const url of endpoints) {
        const res = await tryEndpoint(url);
        if (res) return res;
      }
    }
    return null;
  }
};