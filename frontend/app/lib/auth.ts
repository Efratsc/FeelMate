import { betterAuth } from "better-auth";
import { Pool } from "pg";

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
  },
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
  // Custom table configuration to match existing database schema
  tables: {
    user: "user", // Use existing 'user' table instead of 'users'
    session: "session", // Use existing 'session' table
    verification: "verification", // Use existing 'verification' table
  },
  // Map column names to match existing schema
  columns: {
    user: {
      id: "id",
      email: "email",
      hashedPassword: "hashedPassword", // This might not exist, we'll need to add it
      name: "name",
      emailVerified: "emailVerified",
      image: "image",
      createdAt: "createdAt",
      updatedAt: "updatedAt",
    },
    session: {
      id: "id",
      userId: "userId",
      expiresAt: "expiresAt",
    },
    verification: {
      id: "id",
      userId: "userId",
      expiresAt: "expiresAt",
    },
  },
});