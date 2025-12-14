# Frontend Deployment Guide (Vercel/Netlify)

## Environment Variables Required

Your frontend needs to know where your backend services are deployed. Configure these environment variables:

### Required Variables

1. **NEXT_PUBLIC_AUTH_URL** - Your auth server URL
   - Local: `http://localhost:8080`
   - Vercel: `https://your-auth-server.vercel.app`

2. **NEXT_PUBLIC_API_URL** - Your FastAPI backend URL
   - Local: `http://localhost:8000`
   - Render: `https://your-backend.onrender.com`

## Deployment Steps

### Option 1: Vercel (Recommended)

#### 1. Find Your Auth Server URL
1. Go to your Vercel dashboard
2. Find your **auth-server** project
3. Copy the deployment URL (e.g., `https://auth-server-abc123.vercel.app`)

#### 2. Configure Environment Variables
1. Go to your **frontend** project in Vercel
2. Navigate to **Settings** → **Environment Variables**
3. Add these variables:

```bash
NEXT_PUBLIC_AUTH_URL=https://your-auth-server.vercel.app
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

**Important**: Make sure to select all environments (Production, Preview, Development)

#### 3. Redeploy
1. Go to **Deployments** tab
2. Click on the latest deployment
3. Click **Redeploy** button
4. Wait for deployment to complete

### Option 2: Netlify

#### 1. Configure Environment Variables
1. Go to your Netlify site dashboard
2. Navigate to **Site settings** → **Environment variables**
3. Add the same variables:

```bash
NEXT_PUBLIC_AUTH_URL=https://your-auth-server.vercel.app
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

#### 2. Redeploy
1. Go to **Deploys** tab
2. Click **Trigger deploy** → **Deploy site**
3. Wait for deployment to complete

## Verify Deployment

### 1. Check Environment Variables
After deployment, verify the variables are set:
- Vercel: Settings → Environment Variables
- Netlify: Site settings → Environment variables

### 2. Test the Proxy
Open your deployed frontend and check browser console:
- Should not see any CORS errors
- Auth requests should go to your auth server
- Backend requests should go to your API server

### 3. Test Authentication Flow
1. Try to sign up a new user
2. Check browser network tab:
   - Should see POST to `/api/auth/sign-up/email`
   - Should return 200 (not 404)
3. Check for verification email/console logs

## Troubleshooting

### 404 on /api/auth/*
**Problem**: Frontend can't reach auth server

**Solutions**:
1. Check `NEXT_PUBLIC_AUTH_URL` is set correctly
2. Verify auth server is deployed and accessible
3. Test auth server directly: `https://your-auth-server.vercel.app/health`
4. Redeploy frontend after setting env vars

### CORS Errors
**Problem**: Auth server rejecting requests from frontend

**Solutions**:
1. Check auth server has correct `CORS_ORIGINS` set
2. Include your frontend URL in auth server's `CORS_ORIGINS`
3. Example: `CORS_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.netlify.app`

### Environment Variables Not Working
**Problem**: Changes not taking effect

**Solutions**:
1. **Must redeploy** after adding/changing environment variables
2. Clear browser cache and hard refresh (Cmd+Shift+R / Ctrl+Shift+R)
3. Check variables are set for the correct environment (Production/Preview/Dev)

## Quick Reference

### Local Development (.env.local)
```bash
NEXT_PUBLIC_AUTH_URL=http://localhost:8080
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (Vercel/Netlify)
```bash
NEXT_PUBLIC_AUTH_URL=https://auth-server-xxx.vercel.app
NEXT_PUBLIC_API_URL=https://backend-xxx.onrender.com
```

## Architecture Overview

```
User Browser
    ↓
Frontend (Vercel/Netlify)
    ↓
/api/auth/* → Auth Server (Vercel)
/api/backend/* → FastAPI Backend (Render)
```

The frontend acts as a proxy, routing requests to the appropriate backend service based on the URL path.
