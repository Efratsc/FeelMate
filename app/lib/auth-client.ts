import { createAuthClient } from "better-auth/react";

// Make sure NEXT_PUBLIC_BETTER_AUTH_URL points to your app
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
});


