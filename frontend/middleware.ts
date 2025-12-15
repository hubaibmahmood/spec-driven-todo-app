import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  // In production (HTTPS), browsers add __Secure- prefix to cookies with secure flag
  // In development (HTTP), the cookie name has no prefix
  const sessionToken =
    request.cookies.get("__Secure-better-auth.session_token") ||
    request.cookies.get("better-auth.session_token");

  const isAuthRoute = request.nextUrl.pathname.startsWith("/login") || request.nextUrl.pathname.startsWith("/register");

  // Define protected routes explicitly or protect everything except auth/public
  // Here we assume everything except auth and static assets is protected
  const isPublicRoute = isAuthRoute || request.nextUrl.pathname === '/';

  if (!sessionToken && !isPublicRoute) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (sessionToken && isAuthRoute) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico, favicon.svg (favicon files)
     * - public files (svg, png, jpg, etc.)
     */
    "/((?!api|_next/static|_next/image|favicon|.*\\.svg|.*\\.png|.*\\.jpg|.*\\.jpeg|.*\\.ico|.*\\.webp).*)",
  ],
};
