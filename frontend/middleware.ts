import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  // JWT authentication: Check for refresh_token cookie (httpOnly cookie set by auth-server)
  // This is more secure than checking localStorage (which middleware cannot access)
  const refreshToken = request.cookies.get("refresh_token");

  const isAuthRoute = request.nextUrl.pathname.startsWith("/login") || request.nextUrl.pathname.startsWith("/register");
  const isVerificationRoute = request.nextUrl.pathname.startsWith("/verify-email") || request.nextUrl.pathname.startsWith("/email-verified");
  const isPasswordResetRoute = request.nextUrl.pathname.startsWith("/forgot-password") || request.nextUrl.pathname.startsWith("/reset-password");

  // Define protected routes explicitly or protect everything except auth/public
  // Here we assume everything except auth and static assets is protected
  // Verification routes are public since users don't have a session yet
  // Password reset routes are public since users may not have a session
  const isPublicRoute = isAuthRoute || isVerificationRoute || isPasswordResetRoute || request.nextUrl.pathname === '/';

  if (!refreshToken && !isPublicRoute) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (refreshToken && isAuthRoute) {
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
