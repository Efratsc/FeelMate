"use client";

import React, { useEffect, useState } from "react";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const stored = typeof window !== 'undefined' ? window.localStorage.getItem('feelm-theme') : null;
    if (stored === 'dark' || stored === 'light') {
      setTheme(stored);
    } else if (window?.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
    }
  }, []);

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('feelm-theme', next);
    }
  };

  return (
    <html lang="en" data-theme={theme}>
      <head>
        <style>{`
          :root {
            --page-bg: linear-gradient(160deg, #f0f7ff 0%, #f8f5ff 60%, #fff8f0 100%);
            --text: #111827;
            --muted: #6b7280;
            --border: rgba(0,0,0,0.06);
            --card: rgba(255,255,255,0.7);
            --card-solid: #ffffff;
            --brand: #111827;
            --accent: #6366f1;
            --chip: #eef2ff;
            --ai-bubble: #f9fafb;
          }
          [data-theme="dark"] {
            --page-bg: linear-gradient(160deg, #0b1020 0%, #0f1324 60%, #121826 100%);
            --text: #e5e7eb;
            --muted: #9ca3af;
            --border: rgba(255,255,255,0.12);
            --card: rgba(17, 24, 39, 0.5);
            --card-solid: #0f172a;
            --brand: #f3f4f6;
            --accent: #8b5cf6;
            --chip: #1f2937;
            --ai-bubble: #111827;
          }
          * { box-sizing: border-box; }
        `}</style>
      </head>
      <body
        style={{
          margin: 0,
          background: 'var(--page-bg)',
          color: 'var(--text)',
          fontFamily: "Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <main style={{ flex: 1 }}>{children}</main>
        {/* Floating theme toggle (available on all pages) */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle theme"
          style={{
            position: 'fixed',
            right: 16,
            bottom: 16,
            border: '1px solid var(--border)',
            background: 'var(--card-solid)',
            color: 'var(--text)',
            borderRadius: 12,
            padding: '8px 12px',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0,0,0,0.12)'
          }}
        >
          {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
        </button>
        <footer style={{ textAlign: "center", padding: "16px 12px", color: 'var(--muted)', fontSize: 13 }}>
          You are in a supportive, judgment‑free space. If you are in crisis, please call local emergency services.
        </footer>
      </body>
    </html>
  )
}
