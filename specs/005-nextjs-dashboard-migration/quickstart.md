# Quickstart: Next.js Frontend

**Feature**: `005-nextjs-dashboard-migration`

## Prerequisites

- Node.js 18+
- Backend running (`http://localhost:8000`)
- Auth Server running (`http://localhost:4000`)

## Setup

1. **Navigate to directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Environment Variables**:
   Create `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_AUTH_URL=http://localhost:4000
   ```

## Development

Start the development server:

```bash
npm run dev
```

Visit `http://localhost:3000`.

## Testing

Run unit and integration tests:

```bash
npm test
```
