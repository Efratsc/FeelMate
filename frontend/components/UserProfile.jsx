import { useSession } from "../app/lib/auth-client";
import { useState } from "react";

export default function UserProfile() {
  const { session, signOut } = useSession();
  const [isLoading, setIsLoading] = useState(false);
  const [userSessions, setUserSessions] = useState([]);
  const [showSessions, setShowSessions] = useState(false);

  const fetchUserSessions = async () => {
    if (!session?.user?.id) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8001/api/chat/sessions/${session.user.id}`);
      if (response.ok) {
        const data = await response.json();
        setUserSessions(data.active_sessions || []);
      }
    } catch (error) {
      console.error('Error fetching user sessions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const cleanupUserSessions = async () => {
    if (!session?.user?.id) return;
    
    try {
      const response = await fetch(`http://localhost:8001/api/chat/cleanup-user-sessions/${session.user.id}`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        alert(`Cleaned up ${data.cleaned_count} expired sessions`);
        fetchUserSessions(); // Refresh the list
      }
    } catch (error) {
      console.error('Error cleaning up sessions:', error);
    }
  };

  if (!session) {
    return null;
  }

  return (
    <div style={{ 
      background: "var(--card)", 
      border: "1px solid var(--border)", 
      borderRadius: 16, 
      padding: 20,
      marginBottom: 20
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ margin: 0, color: "var(--text)" }}>User Profile</h3>
        <button
          onClick={() => signOut()}
          style={{
            padding: "8px 16px",
            backgroundColor: "#ef4444",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          Sign Out
        </button>
      </div>

      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: "14px", color: "var(--muted)", marginBottom: "4px" }}>Email</div>
        <div style={{ fontSize: "16px", color: "var(--text)" }}>{session.user.email}</div>
      </div>

      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: "14px", color: "var(--muted)", marginBottom: "4px" }}>User ID</div>
        <div style={{ fontSize: "14px", color: "var(--text)", fontFamily: "monospace" }}>{session.user.id}</div>
      </div>

      <div style={{ borderTop: "1px solid var(--border)", paddingTop: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <h4 style={{ margin: 0, color: "var(--text)", fontSize: "16px" }}>Chat Sessions</h4>
          <button
            onClick={() => {
              setShowSessions(!showSessions);
              if (!showSessions) {
                fetchUserSessions();
              }
            }}
            style={{
              padding: "6px 12px",
              backgroundColor: "#4f46e5",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "12px"
            }}
          >
            {showSessions ? 'Hide' : 'Show'} Sessions
          </button>
        </div>

        {showSessions && (
          <div>
            <div style={{ display: "flex", gap: "8px", marginBottom: 12 }}>
              <button
                onClick={fetchUserSessions}
                disabled={isLoading}
                style={{
                  padding: "6px 12px",
                  backgroundColor: "#059669",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: isLoading ? "not-allowed" : "pointer",
                  fontSize: "12px",
                  opacity: isLoading ? 0.6 : 1
                }}
              >
                {isLoading ? 'Loading...' : 'Refresh'}
              </button>
              <button
                onClick={cleanupUserSessions}
                style={{
                  padding: "6px 12px",
                  backgroundColor: "#dc2626",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "12px"
                }}
              >
                Cleanup Old Sessions
              </button>
            </div>

            {userSessions.length === 0 ? (
              <div style={{ fontSize: "14px", color: "var(--muted)", textAlign: "center", padding: "20px" }}>
                No active chat sessions found.
              </div>
            ) : (
              <div style={{ maxHeight: "300px", overflowY: "auto" }}>
                {userSessions.map((session, index) => (
                  <div
                    key={session.session_id}
                    style={{
                      border: "1px solid var(--border)",
                      borderRadius: "8px",
                      padding: "12px",
                      marginBottom: "8px",
                      backgroundColor: "var(--card-solid)"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                      <div style={{ fontSize: "12px", color: "var(--muted)" }}>
                        Session {index + 1}
                      </div>
                      <div style={{ fontSize: "12px", color: "var(--muted)" }}>
                        {session.message_count} messages
                      </div>
                    </div>
                    
                    {session.current_emotion && (
                      <div style={{ fontSize: "12px", color: "var(--muted)", marginBottom: "4px" }}>
                        Last emotion: {session.current_emotion}
                      </div>
                    )}
                    
                    <div style={{ fontSize: "12px", color: "var(--muted)" }}>
                      Last activity: {new Date(session.last_activity).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
