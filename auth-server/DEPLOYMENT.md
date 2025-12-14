# Auth Server - Vercel Deployment Guide

## Prerequisites

- [x] Vercel account (sign up at https://vercel.com)
- [x] Neon PostgreSQL database (get connection string from https://console.neon.tech)
- [x] Resend account for emails (get API key from https://resend.com)
- [ ] Vercel CLI installed: `npm install -g vercel`

## Quick Start Deployment

### 1. Create Prisma Migration (First Time Only)

```bash
cd auth-server
npx prisma migrate dev --name init
```

This creates your database schema and migration files.

### 2. Install Vercel CLI

```bash
npm install -g vercel
```

### 3. Login to Vercel

```bash
vercel login
```

### 4. Deploy Preview

```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? Select your account
- Link to existing project? **No** (first time)
- Project name? **momentum-auth-server**
- Directory? **./** (press Enter)
- Override settings? **No** (we use vercel.json)

### 5. Configure Environment Variables

Go to Vercel Dashboard → Your Project → Settings → Environment Variables

Add these variables for **Production**, **Preview**, and **Development**:

```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=<generate-with-command-below>
RESEND_API_KEY=re_your_resend_api_key
EMAIL_FROM=noreply@yourdomain.com
FRONTEND_URL=https://your-frontend.vercel.app
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.netlify.app
NODE_ENV=production
PORT=8080
```

**Generate BETTER_AUTH_SECRET:**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 6. Deploy to Production

```bash
vercel --prod
```

### 7. Test Deployment

```bash
# Test health endpoint
curl https://your-project.vercel.app/health

# Expected response:
# {
#   "status": "ok",
#   "timestamp": "2025-12-14T...",
#   "database": "connected"
# }
```

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string from Neon | `postgresql://user:pass@ep-xxx.neon.tech/db` |
| `BETTER_AUTH_SECRET` | ✅ Yes | Random 32+ character secret for JWT | Generate with crypto command above |
| `RESEND_API_KEY` | ✅ Yes | API key from Resend for emails | `re_xxxxxxxxxxxxx` |
| `EMAIL_FROM` | ✅ Yes | Verified sender email address | `noreply@yourdomain.com` |
| `FRONTEND_URL` | ✅ Yes | Your frontend application URL | `https://app.yourdomain.com` |
| `CORS_ORIGINS` | ✅ Yes | Comma-separated allowed origins | `https://app.com,https://www.app.com` |
| `NODE_ENV` | ✅ Yes | Environment mode | `production` |
| `PORT` | ⚠️ Optional | Server port (Vercel auto-assigns) | `8080` |

## Vercel Project Structure

```
auth-server/
├── api/
│   └── index.ts          # Vercel serverless entry point
├── src/
│   ├── app.ts            # Express app configuration
│   ├── index.ts          # Local development server
│   └── ...               # Other source files
├── prisma/
│   ├── schema.prisma     # Database schema
│   └── migrations/       # Migration files
├── dist/                 # Compiled TypeScript (generated)
├── vercel.json           # Vercel configuration
├── .vercelignore         # Files to exclude from deployment
└── package.json          # Dependencies and scripts

```

## Deployment Configuration Files

### vercel.json
Configures Vercel builds and routes. Already configured in your project.

### .vercelignore
Excludes unnecessary files from deployment (already created).

### package.json scripts
- `vercel-build`: Runs during Vercel build process
  - Applies database migrations
  - Generates Prisma client
  - Compiles TypeScript

## Common Issues & Solutions

### Issue: Database Connection Failed

**Solution:**
- Verify `DATABASE_URL` in Vercel environment variables
- Ensure Neon database is running
- Check connection string includes `?sslmode=require`

### Issue: CORS Errors

**Solution:**
- Add your frontend domain to `CORS_ORIGINS`
- Format: `https://domain1.com,https://domain2.com` (no spaces)
- Include all subdomains you need

### Issue: Email Verification Not Sending

**Solution:**
- Verify `RESEND_API_KEY` is correct
- Verify sender email in Resend dashboard
- Check Resend logs for delivery status

### Issue: Build Fails on Vercel

**Solution:**
- Check build logs in Vercel dashboard
- Verify all dependencies in package.json
- Ensure TypeScript compiles locally: `npm run build`

## Local Testing Before Deployment

```bash
# Install dependencies
npm install

# Generate Prisma client
npx prisma generate

# Run migrations
npx prisma migrate deploy

# Build
npm run build

# Test locally
npm start
```

## Continuous Deployment

Vercel automatically deploys when you push to Git:

1. **Main branch** → Production deployment
2. **Other branches** → Preview deployments

### Connect Git Repository

```bash
# In Vercel Dashboard:
# Settings → Git → Connect Git Repository
```

Or link via CLI:
```bash
vercel git connect
```

## Monitoring & Logs

### View Logs
```bash
vercel logs <deployment-url>
```

### In Vercel Dashboard
- Go to your project
- Click "Deployments" tab
- Click on a deployment
- View "Runtime Logs" and "Build Logs"

## Update Deployment

```bash
# After making changes, redeploy:
vercel --prod

# Or push to Git if connected
git push origin main
```

## Rollback Deployment

In Vercel Dashboard:
1. Go to "Deployments"
2. Find previous working deployment
3. Click "..." → "Promote to Production"

## Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS as instructed by Vercel
4. Update `FRONTEND_URL` and `CORS_ORIGINS` to include new domain

## Security Checklist

- [x] `BETTER_AUTH_SECRET` is random and secure (32+ chars)
- [x] Environment variables stored in Vercel (not in code)
- [x] `.env` files are in `.gitignore`
- [x] CORS origins restricted to your domains only
- [x] HTTPS enforced (automatic on Vercel)
- [x] Database uses SSL (`?sslmode=require`)

## Performance Optimization

- [x] Vercel Edge Network (automatic)
- [x] Serverless functions (automatic)
- [x] Build output optimization (TypeScript → JavaScript)
- [ ] Consider Vercel Edge Functions for lower latency (advanced)

## Cost Considerations

**Vercel Free Tier Includes:**
- 100GB bandwidth/month
- 100 serverless function invocations/day
- Unlimited preview deployments

**Monitor usage at:** Vercel Dashboard → Settings → Usage

## Support Resources

- **Vercel Documentation:** https://vercel.com/docs
- **Better-auth Documentation:** https://better-auth.com/docs
- **Prisma Documentation:** https://www.prisma.io/docs
- **Vercel Support:** https://vercel.com/support

## Next Steps After Deployment

1. Update frontend to use production auth server URL
2. Test authentication flow end-to-end
3. Monitor logs for any errors
4. Set up custom domain (if needed)
5. Configure production OAuth providers (Google, GitHub, etc.)
