'use client';

import { useState, useEffect, useCallback, useRef, createContext, useContext } from 'react';
import {
  AssistantRuntimeProvider,
  ThreadPrimitive,
  useMessage,
  useExternalStoreRuntime,
} from "@assistant-ui/react";
import type { AppendMessage, ThreadMessage } from "@assistant-ui/react";
import { getAccessToken } from "@/lib/jwt-auth-client";
import { getUserTimezone } from "@/lib/utils/timezone";
import { sendChatMessageStreaming } from "@/lib/chat/chat-api";
import MarkdownMessage from "./MarkdownMessage";
import { History, MessageSquare, PenSquare, X } from 'lucide-react';

// ---------------------------------------------------------------------------
// Streaming context — passes isRunning + streamingMessageId into message components
// ---------------------------------------------------------------------------
interface StreamingContextValue {
  isRunning: boolean;
  streamingMessageId: string | null;
}

const StreamingContext = createContext<StreamingContextValue>({
  isRunning: false,
  streamingMessageId: null,
});

// ---------------------------------------------------------------------------
// Suggestion prompts
// ---------------------------------------------------------------------------
const suggestions = [
  {
    text: "Add a task to buy groceries tomorrow at 5pm",
    prompt: "Add a task to buy groceries tomorrow at 5pm",
  },
  {
    text: "Show my high priority tasks",
    prompt: "Show my high priority tasks",
  },
  {
    text: "Mark all my grocery tasks as complete",
    prompt: "Mark all my grocery tasks as complete",
  },
  {
    text: "What are my tasks for today?",
    prompt: "What are my tasks for today?",
  },
];

// ---------------------------------------------------------------------------
// Message components — ChatGPT / ChatKit style
// ---------------------------------------------------------------------------
const UserMessage = () => {
  const message = useMessage((s) => s);
  const content = message.content
    .map((part: any) => (part.type === 'text' ? part.text : ''))
    .join('');

  return (
    <div className="flex justify-end mb-3 px-4">
      <div className="max-w-[75%] rounded-3xl bg-[#f4f4f4] px-4 py-2.5 text-sm text-gray-900">
        <div className="whitespace-pre-wrap">{content}</div>
      </div>
    </div>
  );
};

const AssistantMessage = () => {
  const message = useMessage((s) => s);
  const { isRunning, streamingMessageId } = useContext(StreamingContext);

  const rawContent = message.content
    .map((part: any) => (part.type === 'text' ? part.text : ''))
    .join('');

  const isStreaming = isRunning && message.id === streamingMessageId;

  return (
    <div className="flex flex-col mb-4 px-4">
      {/* Small gradient avatar dot above the message */}
      <span className="mb-1.5 h-6 w-6 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex-shrink-0" />
      <div className="text-sm text-gray-900 leading-relaxed">
        <MarkdownMessage content={rawContent} />
        {isStreaming && (
          <span className="inline-block w-[2px] h-[1em] bg-gray-900 ml-0.5 align-middle animate-[blink_1s_step-end_infinite]" />
        )}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface LocalMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: Date;
}

interface Conversation {
  id: number;
  title: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// convertMessage — keeps exact same shape as before
// ---------------------------------------------------------------------------
function convertMessage(msg: LocalMessage): ThreadMessage {
  if (msg.role === 'user') {
    return {
      id: msg.id,
      role: 'user',
      content: [{ type: 'text', text: msg.content }],
      createdAt: msg.createdAt,
      metadata: { custom: {} },
    } as unknown as ThreadMessage;
  }
  return {
    id: msg.id,
    role: 'assistant',
    content: [{ type: 'text', text: msg.content }],
    createdAt: msg.createdAt,
    status: { type: 'complete', reason: 'stop' },
    metadata: { custom: {} },
  } as unknown as ThreadMessage;
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export function MyAssistant() {
  const accessToken = getAccessToken();
  const timezone = getUserTimezone();

  const [inputValue, setInputValue] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  const resizeTextarea = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    const lineHeight = 20;
    const maxHeight = lineHeight * 5;
    el.style.height = Math.min(el.scrollHeight, maxHeight) + 'px';
  };

  // ---------------------------------------------------------------------------
  // API helpers
  // ---------------------------------------------------------------------------
  const fetchConversations = useCallback(async () => {
    if (!accessToken) return;
    setIsLoadingHistory(true);
    try {
      const AI_AGENT_URL = process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002';
      const response = await fetch(`${AI_AGENT_URL}/api/conversations`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  }, [accessToken]);

  const loadConversation = async (id: number) => {
    if (!accessToken) return;
    try {
      const AI_AGENT_URL = process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002';
      const response = await fetch(`${AI_AGENT_URL}/api/conversations/${id}?limit=200`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (response.ok) {
        const data = await response.json();
        // Fix: sort by numeric ID to ensure deterministic order when timestamps collide
        const loaded: LocalMessage[] = (data.messages ?? [])
          .map((msg: any) => ({
            id: String(msg.id),
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            createdAt: new Date(msg.created_at),
          }))
          .sort((a: LocalMessage, b: LocalMessage) => Number(a.id) - Number(b.id));

        if (loaded.length === 0) {
          setCurrentConversationId(id);
          setMessages([]);
        } else {
          setMessages(loaded);
          setCurrentConversationId(id);
        }
        setShowHistory(false);
      }
    } catch (err) {
      console.error('Failed to load conversation:', err);
    }
  };

  const startNewChat = () => {
    abortRef.current?.abort();
    setMessages([]);
    setCurrentConversationId(null);
    setIsRunning(false);
    setStreamingMessageId(null);
    setShowHistory(false);
  };

  // ---------------------------------------------------------------------------
  // Streaming handler
  // ---------------------------------------------------------------------------
  const handleStream = useCallback(
    async (text: string) => {
      if (!text.trim() || !accessToken) return;

      const userMsg: LocalMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: text,
        createdAt: new Date(),
      };
      const assistantId = `assistant-${Date.now() + 1}`;
      const assistantMsg: LocalMessage = {
        id: assistantId,
        role: 'assistant',
        content: '',
        createdAt: new Date(),
      };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsRunning(true);
      setStreamingMessageId(assistantId);

      abortRef.current = new AbortController();

      try {
        await sendChatMessageStreaming(
          text,
          currentConversationId,
          accessToken,
          timezone,
          (delta) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: m.content + delta } : m
              )
            );
          },
          (convId) => {
            setCurrentConversationId(convId);
            window.dispatchEvent(new CustomEvent('tasks-updated'));
            fetchConversations();
          },
          (error) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: `Sorry, something went wrong: ${error}` }
                  : m
              )
            );
          },
          abortRef.current.signal
        );
      } catch (err: any) {
        const isAbort = err?.name === 'AbortError';
        if (!isAbort) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? {
                    ...m,
                    content: `Sorry, something went wrong: ${err?.message ?? String(err)}`,
                  }
                : m
            )
          );
        }
      } finally {
        setIsRunning(false);
        setStreamingMessageId(null);
      }
    },
    [accessToken, timezone, currentConversationId, fetchConversations]
  );

  const onNew = useCallback(
    async (message: AppendMessage) => {
      const text = message.content
        .filter((p): p is { type: 'text'; text: string } => p.type === 'text')
        .map((p) => p.text)
        .join('');
      await handleStream(text);
    },
    [handleStream]
  );

  const runtime = useExternalStoreRuntime({
    isRunning,
    messages,
    convertMessage,
    onNew,
  });

  // Fetch history when sidebar opens
  useEffect(() => {
    if (showHistory) {
      fetchConversations();
    }
  }, [showHistory, fetchConversations]);

  // ---------------------------------------------------------------------------
  // Send helpers
  // ---------------------------------------------------------------------------
  const handleSend = (text: string) => {
    if (!text.trim() || isRunning) return;
    handleStream(text);
    setInputValue('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleStop = () => {
    abortRef.current?.abort();
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <StreamingContext.Provider value={{ isRunning, streamingMessageId }}>
      <AssistantRuntimeProvider runtime={runtime}>
        <div className="relative flex h-full overflow-hidden bg-white">
          {/* ----------------------------------------------------------------
              Main Chat Area
          ---------------------------------------------------------------- */}
          <ThreadPrimitive.Root className="flex flex-col flex-1 h-full min-w-0">

            {/* Minimal top bar: history | new chat */}
            <div className="px-3 py-2 flex items-center justify-between border-b border-gray-100">
              <button
                onClick={() => setShowHistory(true)}
                className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                aria-label="Chat history"
                title="Chat history"
              >
                <History className="h-4 w-4" />
              </button>

              {/* Center dots — purely decorative */}
              <span className="text-[10px] tracking-[0.3em] text-gray-300 select-none">●●●</span>

              <button
                onClick={startNewChat}
                className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                aria-label="New chat"
                title="New chat"
              >
                <PenSquare className="h-4 w-4" />
              </button>
            </div>

            {/* Message list */}
            <ThreadPrimitive.Viewport className="flex-1 overflow-y-auto py-4 bg-white">
              {/* Empty state */}
              <ThreadPrimitive.Empty>
                <div className="flex flex-col items-center justify-center h-full text-center px-6 py-8 space-y-5">
                  {/* Stacked circles avatar */}
                  <div className="relative w-14 h-14 flex-shrink-0">
                    <span className="absolute inset-0 rounded-full bg-gradient-to-br from-purple-400 to-blue-500 opacity-20" />
                    <span className="absolute inset-1.5 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 opacity-50" />
                    <span className="absolute inset-3 rounded-full bg-gradient-to-br from-purple-500 to-blue-600" />
                  </div>

                  <div className="space-y-1">
                    <h3 className="text-lg font-semibold text-gray-900">How can I help?</h3>
                    <p className="text-xs text-gray-400 max-w-[260px] mx-auto">
                      Ask me to manage your tasks, plan your day, or get summaries.
                    </p>
                  </div>

                  {/* 2-column suggestion pills */}
                  <div className="grid grid-cols-2 gap-2 w-full max-w-[320px]">
                    {suggestions.map((s, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => handleSend(s.prompt)}
                        className="text-left px-3 py-2 text-xs border border-gray-200 bg-white rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all text-gray-600 leading-snug shadow-sm"
                      >
                        {s.text}
                      </button>
                    ))}
                  </div>
                </div>
              </ThreadPrimitive.Empty>

              <ThreadPrimitive.Messages
                components={{
                  UserMessage,
                  AssistantMessage,
                }}
              />
            </ThreadPrimitive.Viewport>

            {/* Composer */}
            <div className="bg-white border-t border-gray-100 px-3 py-3">
              <div className="flex items-end gap-2 border border-gray-300 rounded-2xl px-4 py-3 bg-white focus-within:border-gray-400 transition-colors">
                <textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => {
                    setInputValue(e.target.value);
                    resizeTextarea();
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend(inputValue);
                    }
                  }}
                  placeholder="Message assistant…"
                  className="flex-1 bg-transparent resize-none text-sm focus:outline-none placeholder:text-gray-400 text-gray-900 leading-5"
                  rows={1}
                  style={{ maxHeight: '100px', overflowY: 'auto' }}
                />

                {isRunning ? (
                  /* Stop button */
                  <button
                    type="button"
                    onClick={handleStop}
                    className="flex-shrink-0 bg-black text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-gray-800 transition-colors"
                    aria-label="Stop generation"
                  >
                    {/* Square stop icon */}
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-3.5 w-3.5"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                    >
                      <rect x="4" y="4" width="16" height="16" rx="2" />
                    </svg>
                  </button>
                ) : (
                  /* Send button */
                  <button
                    type="button"
                    onClick={() => handleSend(inputValue)}
                    disabled={!inputValue.trim()}
                    className="flex-shrink-0 bg-black text-white rounded-full w-8 h-8 flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:bg-gray-800 transition-colors"
                    aria-label="Send message"
                  >
                    {/* Up-arrow icon */}
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-4 w-4"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth={2.5}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <line x1="12" y1="19" x2="12" y2="5" />
                      <polyline points="5 12 12 5 19 12" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          </ThreadPrimitive.Root>

          {/* ----------------------------------------------------------------
              History Sidebar — slides in from left
          ---------------------------------------------------------------- */}
          <div
            className={`absolute inset-y-0 left-0 z-50 w-full transform bg-white transition-transform duration-300 ease-in-out ${
              showHistory ? 'translate-x-0' : '-translate-x-full'
            }`}
          >
            <div className="flex flex-col h-full">
              {/* Sidebar header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white">
                <h3 className="text-sm font-semibold text-gray-800">Chat History</h3>
                <button
                  onClick={() => setShowHistory(false)}
                  className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                  aria-label="Close history"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* New Chat button */}
              <div className="px-3 pt-3 pb-2">
                <button
                  onClick={startNewChat}
                  className="flex items-center justify-center gap-2 w-full py-2 px-4 bg-gray-900 text-white rounded-xl hover:bg-gray-700 transition-colors font-medium text-sm"
                >
                  <PenSquare className="h-3.5 w-3.5" />
                  New Chat
                </button>
              </div>

              {/* Conversation list */}
              <div className="flex-1 overflow-y-auto px-2 pb-2 space-y-0.5">
                {isLoadingHistory ? (
                  <div className="flex justify-center p-6">
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-gray-700" />
                  </div>
                ) : conversations.length === 0 ? (
                  <p className="text-center text-xs text-gray-400 mt-6">No past conversations</p>
                ) : (
                  conversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => loadConversation(conv.id)}
                      className={`flex items-start gap-3 w-full px-3 py-2.5 text-left rounded-xl transition-all ${
                        currentConversationId === conv.id
                          ? 'bg-gray-100 text-gray-900'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      <MessageSquare
                        className={`h-3.5 w-3.5 mt-0.5 flex-shrink-0 ${
                          currentConversationId === conv.id ? 'text-gray-700' : 'text-gray-400'
                        }`}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium truncate">
                          {conv.title || 'Untitled Chat'}
                        </p>
                        <p className="text-[10px] text-gray-400 mt-0.5">
                          {new Date(conv.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </AssistantRuntimeProvider>
    </StreamingContext.Provider>
  );
}
