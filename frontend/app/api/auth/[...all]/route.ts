import { auth } from "@/lib/auth"; // path to your auth file
import { toNextJsHandler } from "better-auth/next-js";
import { NextResponse } from "next/server";
import { Pool } from "pg";
import crypto from "crypto";

const handler = toNextJsHandler(auth);

export async function GET(request: Request) {
  try {
    console.log("[auth][GET]", request.url);
  } catch {}
  const { pathname } = new URL(request.url);
  // Manual session endpoint: /api/auth/session
  if (pathname.endsWith("/api/auth/session")) {
    try {
      const cookieHeader = request.headers.get("cookie") || "";
      const cookies = Object.fromEntries(
        cookieHeader.split(/;\s*/).filter(Boolean).map(kv => {
          const idx = kv.indexOf("=");
          return idx === -1 ? [kv, ""] : [kv.slice(0, idx), decodeURIComponent(kv.slice(idx + 1))];
        })
      );
      const sessionToken = cookies["auth_session"];
      if (!sessionToken) {
        return NextResponse.json({ session: null }, { status: 200 });
      }
      const pool = new Pool({ connectionString: process.env.DATABASE_URL });
      const client = await pool.connect();
      try {
        const result = await client.query(
          `SELECT s.id as session_id, s."expiresAt" as expires_at, u.id as user_id, u.email, u.name
           FROM "session" s JOIN "user" u ON s."userId" = u.id
           WHERE s.token = $1 AND s."expiresAt" > NOW()`,
          [sessionToken]
        );
        if (result.rows.length === 0) {
          return NextResponse.json({ session: null }, { status: 200 });
        }
        const row = result.rows[0];
        return NextResponse.json({
          session: {
            id: row.session_id,
            expiresAt: row.expires_at,
            user: { id: row.user_id, email: row.email, name: row.name }
          }
        });
      } finally {
        client.release();
        await pool.end();
      }
    } catch (e: any) {
      return NextResponse.json({ error: e.message || "Session error" }, { status: 500 });
    }
  }
  // @ts-ignore - handler has GET
  return handler.GET(request);
}

export async function POST(request: Request) {
  try {
    console.log("[auth][POST]", request.url);
  } catch {}
  const { pathname } = new URL(request.url);
  // Manual sign-up endpoint: /api/auth/sign-up
  if (pathname.endsWith("/api/auth/sign-up")) {
    try {
      const body = await request.json();
      const { email, password, name, image } = body || {};
      if (!email || !password || !name) {
        return NextResponse.json({ error: "Missing name, email or password" }, { status: 400 });
      }
      const pool = new Pool({ connectionString: process.env.DATABASE_URL });
      const client = await pool.connect();
      try {
        // Check existing user
        const existing = await client.query('SELECT id FROM "user" WHERE email = $1', [email]);
        let userId: string;
        if (existing.rows.length > 0) {
          userId = existing.rows[0].id;
        } else {
          userId = crypto.randomUUID();
          await client.query(
            `INSERT INTO "user" (id, name, email, "emailVerified", image, "createdAt", "updatedAt")
             VALUES ($1, $2, $3, $4, $5, NOW(), NOW())`,
            [userId, name, email, false, image || null]
          );
        }

        // Upsert account with hashed password
        const accountId = crypto.randomUUID();
        const hashedPassword = crypto.createHash('sha256').update(password).digest('hex');
        const accountExisting = await client.query(
          'SELECT id FROM "account" WHERE "userId" = $1 AND "providerId" = $2',
          [userId, 'credentials']
        );
        if (accountExisting.rows.length > 0) {
          await client.query(
            'UPDATE "account" SET password = $1, "updatedAt" = NOW() WHERE id = $2',
            [hashedPassword, accountExisting.rows[0].id]
          );
        } else {
          await client.query(
            `INSERT INTO "account" (id, "accountId", "providerId", "userId", password, "createdAt", "updatedAt")
             VALUES ($1, $2, $3, $4, $5, NOW(), NOW())`,
            [accountId, email, 'credentials', userId, hashedPassword]
          );
        }

        return NextResponse.json({ success: true });
      } finally {
        client.release();
        await pool.end();
      }
    } catch (e: any) {
      return NextResponse.json({ error: e.message || "Signup error" }, { status: 500 });
    }
  }
  // Manual sign-in endpoint: /api/auth/sign-in
  if (pathname.endsWith("/api/auth/sign-in")) {
    try {
      const body = await request.json();
      const { email, password } = body || {};
      if (!email || !password) {
        return NextResponse.json({ error: "Missing email or password" }, { status: 400 });
      }
      const pool = new Pool({ connectionString: process.env.DATABASE_URL });
      const client = await pool.connect();
      try {
        const userResult = await client.query(
          'SELECT u.id, u.name, u.email, a.password FROM "user" u JOIN "account" a ON u.id = a."userId" WHERE u.email = $1',
          [email]
        );
        if (userResult.rows.length === 0) {
          return NextResponse.json({ error: "Invalid email or password" }, { status: 401 });
        }
        const user = userResult.rows[0];
        const hashedPassword = crypto.createHash('sha256').update(password).digest('hex');
        if (user.password !== hashedPassword) {
          return NextResponse.json({ error: "Invalid email or password" }, { status: 401 });
        }
        const sessionId = crypto.randomUUID();
        const token = crypto.randomUUID();
        const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
        await client.query(
          `INSERT INTO "session" (id, "expiresAt", token, "createdAt", "updatedAt", "userId")
           VALUES ($1, $2, $3, NOW(), NOW(), $4)`,
          [sessionId, expiresAt, token, user.id]
        );
        const res = NextResponse.json({ success: true });
        res.headers.append('Set-Cookie', `auth_session=${encodeURIComponent(token)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${7*24*60*60}`);
        return res;
      } finally {
        client.release();
        await pool.end();
      }
    } catch (e: any) {
      return NextResponse.json({ error: e.message || "Signin error" }, { status: 500 });
    }
  }
  // @ts-ignore - handler has POST
  return handler.POST(request);
}