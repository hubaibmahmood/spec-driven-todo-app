import { createAuthClient } from "better-auth/react"

// For better-auth client, we need the full auth server URL with /api/auth path
// The auth server mounts better-auth at /api/auth/* (see auth-server/src/app.ts:84)
// Local: http://localhost:8080/api/auth
// Production: NEXT_PUBLIC_AUTH_URL should be set to: https://your-auth-server.vercel.app/api/auth
export const authClient = createAuthClient({
    baseURL: process.env.NEXT_PUBLIC_AUTH_URL
        ? `${process.env.NEXT_PUBLIC_AUTH_URL}/api/auth`
        : "http://localhost:8080/api/auth"
})

export const { signIn, signUp, useSession, signOut } = authClient;
