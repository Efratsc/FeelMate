import { useRouter } from "next/router";

export default function Landing() {
  const router = useRouter();
  return (
    <div style={{
      display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center",
      height: "100vh", background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      color: "white", fontFamily: "Inter, sans-serif", textAlign: "center", padding: 20
    }}>
      <h1 style={{ fontSize: 64, marginBottom: 20 }}>FeelMate</h1>
      <p style={{ fontSize: 22, maxWidth: 600, marginBottom: 40 }}>
        Your AI companion for emotions. Share how you feel and get empathetic responses instantly.
      </p>
      <button
        onClick={() => router.push("/app")}
        style={{
          padding: "15px 40px", fontSize: 20, borderRadius: 12,
          border: "none", backgroundColor: "#f6e05e", color: "#333",
          fontWeight: "bold", cursor: "pointer", transition: "0.3s"
        }}
        onMouseOver={e => e.target.style.backgroundColor = "#ecc94b"}
        onMouseOut={e => e.target.style.backgroundColor = "#f6e05e"}
      >
        Open FeelMate
      </button>
    </div>
  );
}
