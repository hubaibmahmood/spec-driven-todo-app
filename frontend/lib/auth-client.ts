import { createAuthClient } from "better-auth/react"

// Auth requests are proxied through the frontend domain via Netlify redirects
// This ensures cookies are set for the same domain (first-party cookies)
//
// Build/SSR: Use full frontend URL (NEXT_PUBLIC_AUTH_URL should be https://momentum.intevia.cc)
// Client-side: Use relative URL to leverage Netlify proxy
// Development: Direct connection to localhost auth server

function getAuthBaseURL() {
    // Development: connect directly to local auth server
    if (process.env.NODE_ENV === 'development') {
        return "http://localhost:8080/api/auth";
    }

    // Production SSR/Build: need full URL
    // Production Client: use relative URL for proxy
    if (typeof window === 'undefined') {
        // Server-side: use full URL from env var
        return process.env.NEXT_PUBLIC_AUTH_URL
            ? `${process.env.NEXT_PUBLIC_AUTH_URL}/api/auth`
            : "https://momentum.intevia.cc/api/auth";
    } else {
        // Client-side: use relative URL (proxied by Netlify)
        return "/api/auth";
    }
}

export const authClient = createAuthClient({
    baseURL: getAuthBaseURL()
})

export const { signIn, signUp, useSession, signOut } = authClient;
