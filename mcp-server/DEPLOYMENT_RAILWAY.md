# Deploying MCP Server to Railway

This guide details how to deploy the `mcp-server` to [Railway](https://railway.app/).

## Prerequisites

- A [Railway](https://railway.app/) account
- The [Railway CLI](https://docs.railway.app/guides/cli) installed (optional, but recommended)
- Your `backend` service (FastAPI) already deployed (or deployed alongside this service)

## Configuration

The MCP server requires the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SERVICE_AUTH_TOKEN` | **Required**. Must match the token in your backend. | `your-secure-32-char-token` |
| `FASTAPI_BASE_URL` | **Required**. The URL of your deployed backend. | `https://todo-backend-production.up.railway.app` |
| `MCP_LOG_LEVEL` | Optional. Logging level. | `INFO` |
| `PORT` | Optional. Railway automatically provides this. | `3000` |

## Deployment Steps

### Method 1: Deploy via Railway Dashboard

1.  **Create a New Service**:
    - Go to your Railway project.
    - Click "New" -> "GitHub Repo".
    - Select your repository.

2.  **Configure Root Directory**:
    - Since `mcp-server` is in a subdirectory, you must configure the **Root Directory**.
    - Go to "Settings" -> "General" -> "Root Directory".
    - Set it to `/mcp-server`.
    - Railway will detect the `Dockerfile` in that directory automatically.

3.  **Set Environment Variables**:
    - Go to "Variables".
    - Add `SERVICE_AUTH_TOKEN` (copy from your backend configuration).
    - Add `FASTAPI_BASE_URL` (the public URL of your backend service).

4.  **Deploy**:
    - Railway will build the Docker image and deploy the service.
    - Once deployed, Railway will generate a public URL for your MCP server (e.g., `https://mcp-server-production.up.railway.app`).

### Method 2: Deploy via CLI

1.  Login to Railway:
    ```bash
    railway login
    ```

2.  Link to your project:
    ```bash
    railway link
    ```

3.  Deploy the `mcp-server` service:
    ```bash
    # Ensure you are in the root of the repo
    railway up --service mcp-server
    ```
    *(Note: You might need to configure the service root via `railway.toml` or the dashboard first if not detected correctly).*

## Verifying Deployment

1.  **Check Logs**:
    - In Railway, view the deployment logs.
    - You should see: `Starting todo-mcp-server` and `SSE transport listening on 0.0.0.0:PORT`.

2.  **Health Check**:
    - Visit your deployment URL: `https://<your-service-url>/sse` (Note: direct browser access might just hang or return 405 depending on the endpoint, but it verifies connectivity).
    - For MCP, you usually connect via a client (like Claude Desktop) using the SSE URL.

## Connecting Claude Desktop

To use your **deployed** MCP server with Claude Desktop:

1.  Edit your `claude_desktop_config.json`.
2.  Add a new server configuration using the `mcp-server-sse` transport (if supported by your client version) or use a local relay.

**Note:** Currently, Claude Desktop primarily supports local command-based MCP servers. To connect to a remote SSE MCP server, you might need an SSE-to-Stdio bridge or check the latest Claude Desktop documentation for remote server support.

A common pattern for remote deployment is to use a local "relay" script in your config that connects to the remote URL:

```json
"mcpServers": {
  "todo-remote": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sse-client", "https://your-mcp-server.up.railway.app/sse"]
  }
}
```
*(Requires Node.js installed locally)*

## Troubleshooting

-   **"Connection Refused"**: Ensure `FASTAPI_BASE_URL` is correct and accessible from the Railway container.
-   **"Authentication Failed"**: Verify `SERVICE_AUTH_TOKEN` is identical in both `mcp-server` and `backend`.
-   **Build Failures**: Check the `Dockerfile` steps. Ensure `uv.lock` exists and is up to date.
