import { NextRequest, NextResponse } from "next/server";

const BACKEND_SERVICE_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/$/, "");

async function handler(req: NextRequest) {
  if (req.method !== "POST") {
    return NextResponse.json(
      { error: "Method Not Allowed" },
      { status: 405 },
    );
  }

  try {
    const backendHeaders = new Headers(req.headers);

    // Get the session token from the incoming request's cookies
    const cookieHeader = req.headers.get("cookie");
    if (cookieHeader) {
      const sessionTokenMatch = cookieHeader.match(
        /better-auth\.session_token=([^;]+)/,
      );
      if (sessionTokenMatch && sessionTokenMatch[1]) {
        const sessionToken = decodeURIComponent(sessionTokenMatch[1]);
        // Set the Authorization header for the backend request
        backendHeaders.set("Authorization", `Bearer ${sessionToken}`);
      }
    }

    // Clean up headers for the backend request
    backendHeaders.delete("host");
    backendHeaders.delete("connection");
    backendHeaders.delete("cookie"); // Remove cookie header to avoid sending it to the backend

    // We assume the backend has an endpoint to create a chatkit session
    const targetUrl = `${BACKEND_SERVICE_URL}/api/v1/chatkit/session`;
    
    const backendResponse = await fetch(targetUrl, {
      method: "POST",
      headers: backendHeaders,
      body: req.body,
      // @ts-ignore
      duplex: 'half', // Required for streaming request bodies in Node.js fetch
    });

    if (!backendResponse.ok) {
      const errorBody = await backendResponse.text();
      console.error("[ChatKit Secret] Backend error:", errorBody);
      return NextResponse.json(
        { error: `Failed to fetch client_secret from backend. Status: ${backendResponse.status}` },
        { status: backendResponse.status },
      );
    }

    const data = await backendResponse.json();

    if (!data.client_secret) {
        console.error("[ChatKit Secret] Backend did not return a client_secret");
        return NextResponse.json({ error: "Backend did not return a client_secret" }, { status: 500 });
    }

    return NextResponse.json({ client_secret: data.client_secret });
  } catch (error) {
    console.error("[ChatKit Secret] Proxy Error:", error);
    return NextResponse.json({ error: "Proxying error" }, { status: 500 });
  }
}

export { handler as POST };