# Quickstart Guide: Frontend Chat Integration

**Feature**: 009-frontend-chat-integration
**Date**: 2025-12-21
**Phase**: 1 (Design & Contracts)

## Overview

This quickstart guide provides a step-by-step implementation plan for integrating the OpenAI ChatKit SDK into the Next.js frontend. Follow this guide after reviewing the spec, research, and data model documents.

---

## Prerequisites

Before starting implementation:

1. **Backend Ready** (from previous specs):
   - ✅ POST /api/chat endpoint operational (spec 008)
   - ✅ Conversation persistence service deployed (spec 007)
   - ✅ better-auth session management configured (spec 004)
   - ✅ FastAPI backend with task CRUD endpoints (spec 003)

2. **Development Environment**:
   - Node.js 18+ installed
   - Next.js 14+ project initialized
   - TypeScript 5.x configured
   - Tailwind CSS set up (recommended)

3. **Access & Credentials**:
   - Backend API base URL (e.g., `http://localhost:8000`)
   - better-auth domain key (if required by ChatKit SDK)

---

## Implementation Phases

### Phase 1: Install Dependencies

```bash
cd frontend

# Install ChatKit SDK (React integration)
npm install @openai/chatkit-react

# Install date/timezone utilities
npm install date-fns date-fns-tz

# Install testing libraries (if not already present)
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D @playwright/test  # For E2E tests
```

**Verify Installation**:
```bash
npm list @openai/chatkit-react date-fns date-fns-tz
```

---

### Phase 2: Create Type Definitions

**File**: `frontend/types/chat.ts`

```typescript
// Copy type definitions from data-model.md
export interface Message {
  id: string;
  conversationId: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  metadata?: {
    operation?: 'create_task' | 'update_task' | 'delete_task' | 'list_tasks' | 'mark_complete';
    taskId?: string;
    status?: 'pending' | 'success' | 'error';
    errorMessage?: string;
  };
}

export interface Conversation {
  id: string;
  userId: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  hasMore: boolean;
}

export interface ChatApiRequest {
  conversationId?: string;
  message: string;
  timezone: string;
}

export interface ChatApiResponse {
  conversationId: string;
  message: Message;
  operations?: TaskOperation[];
}

export interface TaskOperation {
  type: 'create' | 'update' | 'delete' | 'mark_complete' | 'list';
  taskId?: string;
  task?: Task;
  status: 'success' | 'error';
  errorMessage?: string;
}

// Import Task from existing types or define here
export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  dueDate?: Date;
}
```

---

### Phase 3: Implement Utility Functions

#### 3.1 Timezone Detection

**File**: `frontend/lib/utils/timezone.ts` (create `utils/` directory first)

```typescript
/**
 * Get the user's IANA timezone identifier from browser
 * Example: "America/New_York", "Europe/London", "Asia/Tokyo"
 */
export function getUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}
```

**Test** (TDD - write this first):
```typescript
// frontend/lib/utils/__tests__/timezone.test.ts
import { getUserTimezone } from '../timezone';

describe('getUserTimezone', () => {
  test('returns valid IANA timezone string', () => {
    const timezone = getUserTimezone();
    expect(timezone).toMatch(/^[A-Za-z_]+\/[A-Za-z_]+$/); // e.g., "America/New_York"
  });
});
```

#### 3.2 localStorage Panel State Hook

**File**: `frontend/lib/chat/panel-state.ts`

```typescript
import { useState, useEffect } from 'react';

const PANEL_STATE_KEY = 'chat-panel-state';

interface ChatPanelState {
  isOpen: boolean;
  lastOpenedAt?: Date;
}

export function usePanelState() {
  const [panelState, setPanelState] = useState<ChatPanelState>({
    isOpen: false,
  });

  // Load state from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(PANEL_STATE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setPanelState({
          isOpen: parsed.isOpen ?? false,
          lastOpenedAt: parsed.lastOpenedAt ? new Date(parsed.lastOpenedAt) : undefined,
        });
      } catch (error) {
        console.error('Failed to parse panel state:', error);
      }
    }
  }, []);

  // Save state to localStorage whenever it changes
  const updatePanelState = (updates: Partial<ChatPanelState>) => {
    setPanelState((prev) => {
      const newState = { ...prev, ...updates };
      localStorage.setItem(PANEL_STATE_KEY, JSON.stringify(newState));
      return newState;
    });
  };

  return [panelState, updatePanelState] as const;
}
```

**Test** (TDD):
```typescript
// frontend/lib/chat/__tests__/panel-state.test.ts
import { renderHook, act } from '@testing-library/react';
import { usePanelState } from '../panel-state';

describe('usePanelState', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('initializes with isOpen: false', () => {
    const { result } = renderHook(() => usePanelState());
    expect(result.current[0].isOpen).toBe(false);
  });

  test('persists state to localStorage', () => {
    const { result } = renderHook(() => usePanelState());
    act(() => {
      result.current[1]({ isOpen: true });
    });
    const stored = JSON.parse(localStorage.getItem('chat-panel-state') || '{}');
    expect(stored.isOpen).toBe(true);
  });
});
```

---

### Phase 4: Implement API Client

**File**: `frontend/lib/chat/chat-api.ts` (create `chat/` directory first)

```typescript
import { ChatApiRequest, ChatApiResponse, ConversationHistoryResponse } from '@/types/chat';
import { getUserTimezone } from '../utils/timezone';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Send a chat message to the AI agent
 */
export async function sendChatMessage(
  request: Omit<ChatApiRequest, 'timezone'>,
  sessionToken: string
): Promise<ChatApiResponse> {
  const timezone = getUserTimezone();

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${sessionToken}`,
      'X-Timezone': timezone,
    },
    body: JSON.stringify({
      ...request,
      timezone,
    }),
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Session expired. Please log in again.');
    }
    const error = await response.json();
    throw new Error(error.message || 'Failed to send message');
  }

  const data = await response.json();

  // Convert ISO date strings to Date objects
  data.message.timestamp = new Date(data.message.timestamp);
  if (data.operations) {
    data.operations.forEach((op: any) => {
      if (op.task?.dueDate) {
        op.task.dueDate = new Date(op.task.dueDate);
      }
    });
  }

  return data;
}

/**
 * Fetch conversation history with pagination
 */
export async function fetchConversationHistory(
  conversationId: string,
  sessionToken: string,
  limit: number = 50,
  offset: number = 0
): Promise<ConversationHistoryResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`,
    {
      headers: {
        'Authorization': `Bearer ${sessionToken}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch conversation history');
  }

  const data = await response.json();

  // Convert ISO date strings to Date objects
  data.messages.forEach((msg: any) => {
    msg.timestamp = new Date(msg.timestamp);
  });

  return data;
}

/**
 * Get or create the user's latest conversation
 */
export async function getOrCreateConversation(
  sessionToken: string
): Promise<{ id: string; userId: string; createdAt: Date; updatedAt: Date }> {
  const response = await fetch(`${API_BASE_URL}/api/conversations/latest`, {
    headers: {
      'Authorization': `Bearer ${sessionToken}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to get conversation');
  }

  const data = await response.json();
  return {
    ...data,
    createdAt: new Date(data.createdAt),
    updatedAt: new Date(data.updatedAt),
  };
}
```

**Test** (TDD):
```typescript
// frontend/lib/chat/__tests__/chat-api.test.ts
import { sendChatMessage } from '../chat-api';

describe('sendChatMessage', () => {
  test('includes session token and timezone in request', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        conversationId: 'test-id',
        message: {
          id: 'msg-id',
          conversationId: 'test-id',
          content: 'Response',
          role: 'assistant',
          timestamp: '2025-12-21T14:30:00Z',
        },
      }),
    });

    await sendChatMessage(
      { message: 'add task test' },
      'test-token'
    );

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/chat'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': 'Bearer test-token',
          'X-Timezone': expect.any(String),
        }),
      })
    );
  });
});
```

---

### Phase 5: Build React Components

#### 5.1 ChatToggleButton

**File**: `frontend/components/chat/ChatToggleButton.tsx`

```typescript
'use client';

import { MessageCircle } from 'lucide-react'; // Or any icon library

interface ChatToggleButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export function ChatToggleButton({ isOpen, onClick }: ChatToggleButtonProps) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 z-40 rounded-full bg-blue-600 p-4 text-white shadow-lg hover:bg-blue-700 transition-colors md:hidden"
      aria-label={isOpen ? 'Close chat' : 'Open chat'}
    >
      <MessageCircle className="h-6 w-6" />
    </button>
  );
}
```

**Test** (TDD):
```typescript
// frontend/components/chat/__tests__/ChatToggleButton.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatToggleButton } from '../ChatToggleButton';

test('calls onClick when clicked', async () => {
  const handleClick = jest.fn();
  render(<ChatToggleButton isOpen={false} onClick={handleClick} />);

  await userEvent.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

#### 5.2 ChatMessage Component

**File**: `frontend/components/chat/ChatMessage.tsx` (create `chat/` directory first)

```typescript
'use client';

import { Message } from '@/types/chat';
import { formatInTimeZone } from 'date-fns-tz';
import { getUserTimezone } from '@/lib/utils/timezone';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const timezone = getUserTimezone();

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100'
        }`}
      >
        <p className="text-sm">{message.content}</p>
        <p className="text-xs opacity-70 mt-1">
          {formatInTimeZone(message.timestamp, timezone, 'h:mm a')}
        </p>
        {message.metadata?.status === 'error' && (
          <p className="text-xs text-red-300 mt-1">
            ⚠️ {message.metadata.errorMessage}
          </p>
        )}
      </div>
    </div>
  );
}
```

**Test** (TDD):
```typescript
// frontend/components/chat/__tests__/ChatMessage.test.tsx
import { render, screen } from '@testing-library/react';
import { ChatMessage } from '../ChatMessage';

test('renders user message with correct styling', () => {
  const message = {
    id: '1',
    conversationId: '1',
    content: 'Hello',
    role: 'user' as const,
    timestamp: new Date('2025-12-21T14:30:00Z'),
  };

  render(<ChatMessage message={message} />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
  expect(screen.getByText('Hello').parentElement).toHaveClass('bg-blue-600');
});
```

#### 5.3 ChatPanel (Main Component)

**File**: `frontend/components/chat/ChatPanel.tsx`

```typescript
'use client';

import { useState, useEffect, useRef } from 'react';
import { useSession } from 'better-auth/react'; // Adjust import based on setup
import { Message } from '@/types/chat';
import { sendChatMessage, fetchConversationHistory, getOrCreateConversation } from '@/lib/chat/chat-api';
import { ChatMessage } from './ChatMessage';
import { X } from 'lucide-react';

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  const { session } = useSession();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation on mount
  useEffect(() => {
    if (isOpen && session?.token) {
      loadConversation();
    }
  }, [isOpen, session]);

  const loadConversation = async () => {
    if (!session?.token) return;

    try {
      const conversation = await getOrCreateConversation(session.token);
      setConversationId(conversation.id);

      const history = await fetchConversationHistory(conversation.id, session.token, 50, 0);
      setMessages(history.messages);
      setHasMore(history.hasMore);
      setOffset(50);
      scrollToBottom();
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const loadMoreMessages = async () => {
    if (!conversationId || !session?.token || !hasMore) return;

    setIsLoading(true);
    try {
      const history = await fetchConversationHistory(conversationId, session.token, 50, offset);
      setMessages((prev) => [...history.messages, ...prev]); // Prepend older messages
      setHasMore(history.hasMore);
      setOffset((prev) => prev + 50);
    } catch (error) {
      console.error('Failed to load more messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !session?.token) return;

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      conversationId: conversationId || '',
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(
        {
          conversationId: conversationId || undefined,
          message: inputValue,
        },
        session.token
      );

      setConversationId(response.conversationId);
      setMessages((prev) => [...prev.filter((m) => m.id !== userMessage.id), response.message]);

      // Handle task operations (update shared task context if applicable)
      if (response.operations) {
        // TODO: Call TaskContext methods to update task list
      }

      scrollToBottom();
    } catch (error: any) {
      console.error('Failed to send message:', error);
      alert(error.message || 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  if (!isOpen) return null;

  return (
    <div
      className={`fixed z-50 bg-white dark:bg-gray-900 shadow-xl transition-transform duration-300 ease-in-out
        md:right-0 md:top-0 md:h-screen md:w-96 md:translate-x-${isOpen ? '0' : 'full'}
        max-md:inset-0 max-md:translate-y-${isOpen ? '0' : 'full'}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b p-4">
        <h2 className="text-lg font-semibold">Chat Assistant</h2>
        <button onClick={onClose} className="hover:bg-gray-100 p-2 rounded-full">
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 h-[calc(100vh-140px)]">
        {hasMore && (
          <button
            onClick={loadMoreMessages}
            disabled={isLoading}
            className="w-full mb-4 text-sm text-blue-600 hover:underline"
          >
            {isLoading ? 'Loading...' : 'Load More'}
          </button>
        )}
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSendMessage} className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
```

**Test** (TDD):
```typescript
// frontend/components/chat/__tests__/ChatPanel.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatPanel } from '../ChatPanel';

jest.mock('better-auth/react', () => ({
  useSession: () => ({ session: { token: 'test-token' } }),
}));

jest.mock('@/lib/chat/chat-api', () => ({
  getOrCreateConversation: jest.fn().mockResolvedValue({ id: 'conv-1', userId: 'user-1', createdAt: new Date(), updatedAt: new Date() }),
  fetchConversationHistory: jest.fn().mockResolvedValue({ messages: [], hasMore: false, total: 0, limit: 50, offset: 0 }),
  sendChatMessage: jest.fn().mockResolvedValue({
    conversationId: 'conv-1',
    message: {
      id: 'msg-1',
      conversationId: 'conv-1',
      content: 'Response',
      role: 'assistant',
      timestamp: new Date(),
    },
  }),
}));

test('renders chat panel when open', () => {
  render(<ChatPanel isOpen={true} onClose={jest.fn()} />);
  expect(screen.getByText('Chat Assistant')).toBeInTheDocument();
});

test('sends message when form is submitted', async () => {
  const { sendChatMessage } = require('@/lib/chat/chat-api');
  render(<ChatPanel isOpen={true} onClose={jest.fn()} />);

  const input = screen.getByPlaceholderText('Type a message...');
  const sendButton = screen.getByText('Send');

  await userEvent.type(input, 'add task test');
  await userEvent.click(sendButton);

  await waitFor(() => {
    expect(sendChatMessage).toHaveBeenCalledWith(
      expect.objectContaining({ message: 'add task test' }),
      'test-token'
    );
  });
});
```

---

### Phase 6: Integrate into Dashboard Layout

**File**: `frontend/app/(dashboard)/layout.tsx` (dashboard layout)

Update the existing dashboard layout to add chat components:

```typescript
"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { useSession, signOut } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
// NEW IMPORTS
import { ChatPanel } from "@/components/chat/ChatPanel";
import { ChatToggleButton } from "@/components/chat/ChatToggleButton";
import { usePanelState } from "@/lib/chat/panel-state";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { data: session } = useSession();
  const [user, setUser] = useState<{ name: string; email: string; image?: string | null } | null>(null);
  const router = useRouter();

  // NEW: Chat panel state
  const [panelState, updatePanelState] = usePanelState();

  useEffect(() => {
    if (session?.user) {
      setUser({
        name: session.user.name,
        email: session.user.email,
        image: session.user.image
      });
    }
  }, [session]);

  const handleLogout = async () => {
    await signOut();
    router.push("/login");
  };

  // NEW: Toggle chat panel
  const toggleChatPanel = () => {
    updatePanelState({
      isOpen: !panelState.isOpen,
      lastOpenedAt: new Date(),
    });
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onLogout={handleLogout}
        user={user}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header onMenuClick={() => setIsSidebarOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <div className="max-w-7xl mx-auto space-y-8">
            {children}
          </div>
        </main>
      </div>

      {/* NEW: Chat Panel (desktop: side panel, mobile: full-screen overlay) */}
      <ChatPanel
        isOpen={panelState.isOpen}
        onClose={() => updatePanelState({ isOpen: false })}
      />

      {/* NEW: Chat Toggle Button (shows on mobile, can also show on desktop) */}
      <ChatToggleButton
        isOpen={panelState.isOpen}
        onClick={toggleChatPanel}
      />
    </div>
  );
}
```

**Changes Made**:
1. Import chat components and `usePanelState` hook
2. Add chat panel state management
3. Add `toggleChatPanel` function
4. Render `<ChatPanel />` at the end (after main content, outside flex-1 div)
5. Render `<ChatToggleButton />` for opening/closing the panel

---

### Phase 7: Write E2E Tests

**File**: `frontend/__tests__/e2e/chat-workflow.spec.ts` (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Chat Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login first (adjust based on your auth flow)
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('User creates task via chat and sees it in task list', async ({ page }) => {
    // Open chat panel (mobile button or desktop panel)
    await page.click('button[aria-label="Open chat"]');

    // Wait for chat panel to appear
    await expect(page.locator('text=Chat Assistant')).toBeVisible();

    // Send message to create task
    await page.fill('input[placeholder="Type a message..."]', 'add task review PRs by Friday');
    await page.click('button:has-text("Send")');

    // Wait for AI response
    await expect(page.locator('text=I\'ve created a task')).toBeVisible({ timeout: 5000 });

    // Verify task appears in main task list
    await expect(page.locator('text=review PRs')).toBeVisible({ timeout: 3000 });
  });

  test('Chat panel state persists across page reloads', async ({ page }) => {
    // Open chat panel
    await page.click('button[aria-label="Open chat"]');
    await expect(page.locator('text=Chat Assistant')).toBeVisible();

    // Reload page
    await page.reload();

    // Panel should still be open (localStorage persistence)
    await expect(page.locator('text=Chat Assistant')).toBeVisible();
  });
});
```

---

## Testing Checklist

Run tests in TDD order:

1. **Unit Tests** (fast feedback):
   ```bash
   npm test -- --watch
   ```
   - ✅ `timezone.test.ts`
   - ✅ `panel-state.test.ts`
   - ✅ `chat-api.test.ts`

2. **Component Tests**:
   ```bash
   npm test components/chat
   ```
   - ✅ `ChatToggleButton.test.tsx`
   - ✅ `ChatMessage.test.tsx`
   - ✅ `ChatPanel.test.tsx`

3. **E2E Tests** (full integration):
   ```bash
   npx playwright test
   ```
   - ✅ User creates task via chat
   - ✅ Chat panel state persists
   - ✅ Conversation history loads on panel open
   - ✅ Real-time task updates in todo list

---

## Validation Checklist

Before marking implementation complete:

- [ ] All unit tests pass (100% coverage for utility functions)
- [ ] All component tests pass (80%+ coverage)
- [ ] All E2E tests pass (6 user stories from spec)
- [ ] Chat panel is responsive (tested on 320px and 1920px)
- [ ] Session token is included in all API requests
- [ ] Timezone header is sent correctly
- [ ] Conversation history loads within 1 second
- [ ] Messages render within 200ms after API response
- [ ] Panel animation completes within 300ms
- [ ] localStorage persists panel open/closed state
- [ ] Error messages are user-friendly and actionable
- [ ] TypeScript compiles with no errors
- [ ] ESLint passes with no warnings

---

## Architecture Decision Points

As you implement, document these decisions if significant tradeoffs exist:

1. **State Management**: If you add Redux/Zustand, create ADR for why React Context was insufficient
2. **ChatKit SDK Customization**: If you build custom UI instead of using ChatKit, document rationale
3. **Real-time Updates**: If you implement WebSocket instead of optimistic UI, document why
4. **Mobile Breakpoint**: If you change from 768px to another value, justify the choice

Use `/sp.adr <decision-title>` to create Architecture Decision Records when prompted.

---

## Next Steps

After completing implementation:

1. Run `/sp.tasks` to generate detailed task breakdown with test cases
2. Follow Red-Green-Refactor cycle for each task
3. Create PHR (Prompt History Record) after each major milestone
4. Request code review after each user story is complete
5. Deploy to staging environment for manual QA

---

**Questions?** Refer to:
- **spec.md**: User stories and requirements
- **research.md**: Technology decisions and alternatives
- **data-model.md**: TypeScript types and validation rules
- **contracts/chat-api.yaml**: API endpoint specifications

Good luck! 🚀
