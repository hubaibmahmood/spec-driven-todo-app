# Frontend - Task Management Dashboard

A Next.js-based frontend for managing tasks with AI-powered chat assistance. Built with TypeScript, React 18+, and Tailwind CSS.

## Features

### 🎯 Task Management (Specs 001-003)
- ✅ CRUD operations for tasks (create, read, update, delete, mark complete)
- ✅ Priority levels and due dates
- ✅ Responsive dashboard UI

### 🔐 Authentication (Spec 004)
- ✅ Better-auth integration for secure login/register
- ✅ Session management with Bearer token authentication
- ✅ Email verification

### 💬 AI Chat Integration (Spec 009)
- ✅ **Floating Chat Widget**: Collapsible chat panel for natural language task management
- ✅ **Processing Indicators**: Shows "Processing..." while AI agent works
- ✅ **Conversation History**: Persistent chat sessions across page navigation
- ✅ **Timezone-Aware**: Handles dates/times in user's local timezone
- ✅ **Optimistic UI**: Instant visual feedback with backend sync
- ✅ **Error Handling**: Clear error messages with ⚠️ icons when operations fail
- ✅ **Real-Time Updates**: Dashboard cards update instantly without page refresh
- ✅ **Event-Driven Architecture**: Custom events sync UI across all components

## Technology Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript 5.x
- **UI**: React 18+, Tailwind CSS
- **Authentication**: better-auth (client SDK)
- **State Management**: React Context API
- **Date Handling**: date-fns, date-fns-tz

## Getting Started

### 1. Installation

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Create a `.env.local` file:

```env
# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AI_AGENT_URL=http://localhost:8002
NEXT_PUBLIC_AUTH_URL=http://localhost:3002
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Recent Updates

### Phase 6: Real-Time Feedback (Spec 009)
- ✅ Processing indicators while AI agent works ("Processing your request...")
- ✅ Automatic task list refresh after chat operations
- ✅ Error handling with clear warning messages

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run test         # Run Jest tests
npm run test:watch   # Run tests in watch mode
```

## Authentication

The frontend integrates with better-auth for authentication. Users must log in to access the dashboard and chat features.

Session tokens are automatically included in all API requests via the `useSession()` hook.

## Chat Features

### Natural Language Commands
- "Add a task to buy groceries tomorrow at 5pm"
- "Show my high priority tasks"
- "Mark the first task as complete"
- "Update the second task to high priority"

### Chat Panel
- **Location**: Bottom-right floating widget
- **Toggle**: Click chat icon to open/close
- **Keyboard**: ESC to close
- **Persistence**: Panel state saved in localStorage
- **Responsive**: Full-screen on mobile, side panel on desktop

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Better Auth Docs](https://www.better-auth.com/)
- [Tailwind CSS](https://tailwindcss.com/)
