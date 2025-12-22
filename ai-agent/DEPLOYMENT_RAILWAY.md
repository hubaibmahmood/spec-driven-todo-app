# Deploying AI-Agent to Railway

This guide details how to deploy the `ai-agent` service to [Railway](https://railway.app/).

## Prerequisites

- A [Railway](https://railway.app/) account
- The [Railway CLI](https://docs.railway.app/guides/cli) installed (optional)
- Your `backend` service (FastAPI) already deployed
- Neon PostgreSQL database accessible
- Gemini API key from Google AI Studio

## Configuration

The AI-Agent requires the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | **Required**. PostgreSQL connection string. | `postgresql+asyncpg://user:pass@host/db` |
| `SERVICE_AUTH_TOKEN` | **Required**. Must match backend token. | `your-secure-32-char-token` |
| `AGENT_GEMINI_API_KEY` | **Required**. Your Gemini API key. | `AIzaSy...` |
| `AGENT_MCP_SERVER_URL` | **Required**. URL of your deployed MCP server. | `https://mcp-server.up.railway.app/mcp` |
| `AGENT_MCP_TIMEOUT` | Optional. MCP request timeout. | `10` |
| `AGENT_MCP_RETRY_ATTEMPTS` | Optional. MCP retry attempts. | `3` |
| `AGENT_TEMPERATURE` | Optional. AI response temperature. | `0.7` |
| `AGENT_TOKEN_BUDGET` | Optional. Max tokens per conversation. | `800000` |
| `AGENT_SYSTEM_PROMPT` | Optional. Custom system prompt. | See `.env.example` |
| `ENV` | Optional. Environment name. | `production` |
| `LOG_LEVEL` | Optional. Logging level. | `INFO` |
| `PORT` | Optional. Railway automatically provides this. | `8000` |

## Deployment Steps

### Method 1: Deploy via Railway Dashboard

1.  **Create a New Service**:
    - Go to your Railway project.
    - Click "New" → "GitHub Repo".
    - Select your repository.

2.  **Configure Root Directory**:
    - Go to "Settings" → "General" → "Root Directory".
    - Set to `/ai-agent`.
    - Railway will detect the `Dockerfile` automatically.

3.  **Set Environment Variables** in "Variables" tab:
    - `DATABASE_URL` - Your Neon PostgreSQL connection string (use `postgresql+asyncpg://`)
    - `SERVICE_AUTH_TOKEN` - Match your backend token
    - `AGENT_GEMINI_API_KEY` - Your Gemini API key
    - `AGENT_MCP_SERVER_URL` - Your deployed MCP server URL
    - Add optional variables as needed

4.  **Deploy**:
    - Railway will build the Docker image and run migrations automatically.
    - The service will be available at a public URL like `https://ai-agent-production.up.railway.app`.

### Method 2: Deploy via CLI

```bash
# Login
railway login

# Link project
railway link

# Deploy
railway up --service ai-agent
```

## Verifying Deployment

1.  **Check Logs**:
    - View deployment logs in Railway.
    - You should see: `Alembic upgrade` output, then `Uvicorn running on...`.

2.  **Health Check**:
    - Visit: `https://<your-service-url>/health`
    - Should return: `{"status": "healthy"}`

3.  **Test Root Endpoint**:
    - Visit: `https://<your-service-url>/`
    - Should return: `{"message": "AI Agent - Chat Persistence Service", "version": "0.1.0"}`

## CORS Configuration

Update `ai-agent/src/ai_agent/main.py` to include your frontend's production URL:

```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:3001",
    "https://your-frontend.vercel.app",  # Add your production frontend URL
],
```

## Troubleshooting

-   **"Connection Refused to Database"**: Verify `DATABASE_URL` is correct and Neon allows connections.
-   **"Gemini API Error"**: Check `AGENT_GEMINI_API_KEY` is valid.
-   **"MCP Connection Failed"**: Ensure `AGENT_MCP_SERVER_URL` points to your deployed MCP server.
-   **Migration Failures**: Check database permissions and that tables don't conflict with existing schemas.
