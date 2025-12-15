import { createAuthClient } from "better-auth/react"

// Auth requests go to the frontend domain and are proxied to auth server
// Netlify redirects /api/auth/* → spec-driven-todo-app.vercel.app/api/auth/*
// This ensures cookies are set for the frontend domain (same-origin)

function getAuthBaseURL() {
    // Development: connect directly to local auth server
    if (process.env.NODE_ENV === 'development') {
        return "http://localhost:8080/api/auth";
    }

    // Production: use frontend URL (proxied by Netlify to auth server)
    // better-auth requires absolute URL, not relative
    return process.env.NEXT_PUBLIC_AUTH_URL
        ? `${process.env.NEXT_PUBLIC_AUTH_URL}/api/auth`
        : "https://momentum.intevia.cc/api/auth";
}

export const authClient = createAuthClient({
    baseURL: getAuthBaseURL()
})

export const { signIn, signUp, useSession, signOut } = authClient;
