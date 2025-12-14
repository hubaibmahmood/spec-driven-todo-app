import { NextRequest, NextResponse } from "next/server";

const AUTH_SERVICE_URL = (
  process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:8080"
).replace(/\/$/, "");
const BACKEND_SERVICE_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/$/, "");

async function proxyRequest(request: NextRequest) {


  const urlParts = request.nextUrl.pathname.split("/").filter(Boolean);

  let targetHost: string;
  let newPathname: string;

  if (urlParts.length < 2) {
    return NextResponse.json({ error: "Invalid API route" }, { status: 400 });
  }

  const servicePrefix = urlParts[1];

  if (servicePrefix === "auth") {
    targetHost = AUTH_SERVICE_URL;
    newPathname = `/${urlParts.join("/")}`;
  } else if (servicePrefix === "backend") {
    targetHost = BACKEND_SERVICE_URL;
    newPathname = `/${urlParts.slice(2).join("/")}`;
  } else {
    return NextResponse.json(
      { error: `Unknown service prefix: ${servicePrefix}` },
      { status: 404 },
    );
  }

  const targetUrl = `${targetHost}${newPathname}${request.nextUrl.search}`;

  try {
    const headers = new Headers(request.headers);
    headers.delete("host");
    headers.delete("connection");

    // Extract better-auth.session_token from the Cookie header and convert to Authorization: Bearer
    const cookieHeader = headers.get("cookie");



    if (cookieHeader) {
      const sessionTokenMatch = cookieHeader.match(
        /better-auth\.session_token=([^;]+)/,
      );
      if (sessionTokenMatch && sessionTokenMatch[1]) {
        const sessionToken = decodeURIComponent(sessionTokenMatch[1]);
        headers.set("Authorization", `Bearer ${sessionToken}`);

      }
    }

    const body =
      request.method !== "GET" && request.method !== "HEAD"
        ? await request.blob()
        : undefined;



    const response = await fetch(targetUrl, {
      method: request.method,
      headers: headers,
      body: body,
      redirect: "manual",
      cache: "no-store",
    });



    // Handle redirects
    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get("Location");
      if (location) {
        const redirectUrl = new URL(location, targetHost);

        // For 307/308 redirects from FastAPI (trailing slash redirects), follow them transparently
        if (
          (response.status === 307 || response.status === 308) &&
          redirectUrl.origin === targetHost
        ) {
          // Re-fetch with the redirected URL
          const redirectResponse = await fetch(redirectUrl.toString(), {
            method: request.method,
            headers: headers,
            body: body,
            cache: "no-store",
          });

          // Handle 204 No Content responses correctly
          const shouldHaveRedirectBody = redirectResponse.status !== 204 && redirectResponse.status !== 304 && redirectResponse.status >= 200;
          const nextResponse = shouldHaveRedirectBody
            ? new NextResponse(await redirectResponse.arrayBuffer(), {
                status: redirectResponse.status,
                statusText: redirectResponse.statusText,
              })
            : new NextResponse(null, {
                status: redirectResponse.status,
                statusText: redirectResponse.statusText,
              });

          redirectResponse.headers.forEach((value, key) => {
            if (
              key.toLowerCase() !== "content-encoding" &&
              key.toLowerCase() !== "content-length"
            ) {
              nextResponse.headers.set(key, value);
            }
          });

          return nextResponse;
        }

        // Normal redirect rewriting for same-origin backend redirects
        if (redirectUrl.origin === targetHost) {
          const newLocation = new URL(
            redirectUrl.pathname + redirectUrl.search,
            request.nextUrl.origin,
          ).toString();
          return NextResponse.redirect(newLocation);
        }
        return NextResponse.redirect(location);
      }
    }

    // Handle 204 No Content and similar responses that must not have a body
    const shouldHaveBody = response.status !== 204 && response.status !== 304 && response.status >= 200;

    const nextResponse = shouldHaveBody
      ? new NextResponse(await response.arrayBuffer(), {
          status: response.status,
          statusText: response.statusText,
        })
      : new NextResponse(null, {
          status: response.status,
          statusText: response.statusText,
        });

    // Forward headers
    response.headers.forEach((value, key) => {
      if (
        key.toLowerCase() !== "content-encoding" &&
        key.toLowerCase() !== "content-length"
      ) {
        nextResponse.headers.set(key, value);
      }
    });

    return nextResponse;
  } catch (error) {
    console.error("[Generic Proxy] Error:", error);
    return NextResponse.json({ error: "Generic Proxy Error" }, { status: 500 });
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const DELETE = proxyRequest;
export const PATCH = proxyRequest;
