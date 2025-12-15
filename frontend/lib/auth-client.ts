import { createAuthClient } from "better-auth/react"

// Auth requests are proxied through the frontend domain via Netlify redirects
// This ensures cookies are set for the same domain (first-party cookies)
// Production: /api/auth/* → proxied to auth server via netlify.toml
// Development: Direct connection to localhost:8080/api/auth
export const authClient = createAuthClient({
    baseURL: process.env.NODE_ENV === 'production'
        ? "/api/auth"  // Relative URL - proxied by Netlify
        : "http://localhost:8080/api/auth"  // Direct connection for localhost
})

export const { signIn, signUp, useSession, signOut } = authClient;
