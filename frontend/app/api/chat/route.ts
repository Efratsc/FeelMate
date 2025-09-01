import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  // Extract data from the Vercel AI request
  const { messages, user_id, session_id } = await req.json();
  
  // Get the most recent user message
  const lastUserMessage = messages
    .filter((m: any) => m.role === 'user')
    .pop()?.content || '';

  try {
    // Call your EXISTING FastAPI backend
    const response = await fetch('http://localhost:8001/api/chat/send-message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: lastUserMessage,
        user_id: user_id,
        session_id: session_id,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.statusText}`);
    }

    const data = await response.json();

    // Return the response in the format expected by the frontend
    return new Response(JSON.stringify({
      response: data.response || data.message || 'No response received',
      emotion: data.emotion,
      severity: data.severity,
      confidence: data.confidence,
      needs_help: data.needs_help,
      resources: data.resources || [],
      session_id: data.session_id,
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': data.session_id || '',
      },
    });

  } catch (error) {
    console.error('API route error:', error);
    return new Response(JSON.stringify({
      error: 'Failed to process message',
      details: error instanceof Error ? error.message : 'Unknown error',
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}