/**
 * Auth Server Proxy
 *
 * Proxies auth requests to the auth server (localhost:8080) to avoid cross-origin cookie issues.
 * This allows the frontend to make same-origin requests while cookies are properly forwarded.
 */

import { NextRequest, NextResponse } from 'next/server';

const AUTH_SERVER_URL = process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:8080';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

async function proxyRequest(request: NextRequest, pathSegments: string[]) {
  try {
    const path = pathSegments.join('/');
    const url = `${AUTH_SERVER_URL}/api/${path}`;

    // Get request body if present
    let body: string | undefined;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      try {
        body = await request.text();
      } catch {
        // No body
      }
    }

    // Forward the request to auth server
    const response = await fetch(url, {
      method: request.method,
      headers: {
        'Content-Type': request.headers.get('Content-Type') || 'application/json',
        // Forward cookies from the request
        'Cookie': request.headers.get('Cookie') || '',
      },
      body: body,
    });

    // Get response body
    const responseBody = await response.text();

    // Create response with same status
    const nextResponse = new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
      },
    });

    // Forward Set-Cookie headers from auth server to client
    const setCookieHeaders = response.headers.getSetCookie();
    setCookieHeaders.forEach((cookie) => {
      nextResponse.headers.append('Set-Cookie', cookie);
    });

    return nextResponse;
  } catch (error) {
    console.error('Auth proxy error:', error);
    return NextResponse.json(
      { error: 'Proxy error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
