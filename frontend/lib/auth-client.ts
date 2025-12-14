import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
    // Use the frontend's own API proxy route
    // The proxy at /api/[...all]/route.ts will forward to the auth server
    baseURL: "/api/auth"
})

export const { signIn, signUp, useSession, signOut } = authClient;
