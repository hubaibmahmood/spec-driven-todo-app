import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const token = searchParams.get("token");
  const callbackURL = searchParams.get("callbackURL");

  if (!token) {
    // Redirect to error page if no token
    const redirectUrl = callbackURL || "/email-verified?error=missing-token";
    return NextResponse.redirect(new URL(redirectUrl, request.url));
  }

  try {
    // Forward the verification request to the auth server
    // INTERNAL_AUTH_URL is used for server-side (container-to-container) communication
    // NEXT_PUBLIC_AUTH_URL is the public URL used by the browser
    const authServerUrl = process.env.INTERNAL_AUTH_URL || process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3002";
    const verifyResponse = await fetch(
      `${authServerUrl}/api/auth/verify-email?token=${token}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (verifyResponse.ok) {
      // Verification successful - redirect to callback URL or default success page
      const redirectUrl = callbackURL || "/email-verified?verified=true";
      return NextResponse.redirect(new URL(redirectUrl, request.url));
    } else {
      // Check for specific error types
      const errorData = await verifyResponse.json().catch(() => ({}));

      if (errorData.error === "EXPIRED_TOKEN" || errorData.message?.includes("expired")) {
        return NextResponse.redirect(
          new URL("/email-verified?error=token-expired", request.url)
        );
      } else if (errorData.error === "ALREADY_VERIFIED") {
        return NextResponse.redirect(
          new URL("/email-verified?verified=already", request.url)
        );
      } else {
        return NextResponse.redirect(
          new URL("/email-verified?error=invalid-token", request.url)
        );
      }
    }
  } catch (error) {
    console.error("Email verification error:", error);
    return NextResponse.redirect(
      new URL("/email-verified?error=server-error", request.url)
    );
  }
}
