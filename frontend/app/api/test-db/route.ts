import { NextRequest, NextResponse } from "next/server";
import { Pool } from "pg";

export async function GET(request: NextRequest) {
  try {
    console.log("Testing database connection...");
    
    const pool = new Pool({
      connectionString: process.env.DATABASE_URL,
    });
    
    const client = await pool.connect();
    console.log("Database connected successfully");
    
    // Test query to see if tables exist
    const result = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name
    `);
    
    console.log("Tables found:", result.rows);
    
    client.release();
    await pool.end();
    
    return NextResponse.json({ 
      success: true, 
      tables: result.rows.map(row => row.table_name),
      message: "Database connection successful"
    });
    
  } catch (error: any) {
    console.error('Database test error:', error);
    return NextResponse.json({ 
      success: false, 
      error: error.message 
    }, { status: 500 });
  }
}
