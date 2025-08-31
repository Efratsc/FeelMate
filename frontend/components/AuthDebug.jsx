import { useSession } from "../app/lib/auth-client";
import { useState, useEffect } from "react";

export default function AuthDebug() {
  const { session, isLoading } = useSession();
  const [debugInfo, setDebugInfo] = useState({});

  useEffect(() => {
    setDebugInfo({
      hasSession: !!session,
      sessionData: session,
      isLoading,
      timestamp: new Date().toISOString()
    });
  }, [session, isLoading]);

  if (process.env.NODE_ENV === 'production') {
    return null; // Don't show debug info in production
  }

  return (
    <div style={{
      position: 'fixed',
      top: 10,
      left: 10,
      background: 'rgba(0,0,0,0.8)',
      color: 'white',
      padding: '10px',
      borderRadius: '8px',
      fontSize: '12px',
      fontFamily: 'monospace',
      zIndex: 9999,
      maxWidth: '300px'
    }}>
      <div><strong>Auth Debug:</strong></div>
      <div>Loading: {isLoading ? 'true' : 'false'}</div>
      <div>Has Session: {debugInfo.hasSession ? 'true' : 'false'}</div>
      <div>User ID: {session?.user?.id || 'none'}</div>
      <div>Email: {session?.user?.email || 'none'}</div>
      <div>Time: {debugInfo.timestamp}</div>
    </div>
  );
}