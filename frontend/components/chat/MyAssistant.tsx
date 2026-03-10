'use client';

import { useState } from 'react';
import { 
  AssistantRuntimeProvider,
  ThreadPrimitive,
  useMessage
} from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { useChat } from "@ai-sdk/react";
import { getAccessToken } from "@/lib/jwt-auth-client";
import { getUserTimezone } from "@/lib/utils/timezone";
import MarkdownMessage from "./MarkdownMessage";

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
  }
];

const UserMessage = () => {
  const message = useMessage((s) => s);
  const content = message.content.map((part: any) => {
    if (part.type === 'text') return part.text;
    return '';
  }).join('');

  return (
    <div className="flex justify-end mb-4">
      <div className="max-w-[80%] rounded-2xl px-4 py-2 bg-blue-600 text-white shadow-sm">
        <div className="whitespace-pre-wrap text-sm">{content}</div>
      </div>
    </div>
  );
};

const AssistantMessage = () => {
  const message = useMessage((s) => s);
  const content = message.content.map((part: any) => {
    if (part.type === 'text') return part.text;
    return '';
  }).join('');

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[80%] rounded-2xl px-4 py-2 bg-gray-100 text-gray-900 shadow-sm border border-gray-200">
        <MarkdownMessage content={content} />
      </div>
    </div>
  );
};

export function MyAssistant() {
  const accessToken = getAccessToken();
  const timezone = getUserTimezone();
  const [inputValue, setInputValue] = useState('');

  // Initialize Vercel AI SDK useChat
  const chat = useChat({
    // @ts-ignore
    api: `${process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002'}/api/chat/stream`,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'X-Timezone': timezone,
    },
    onResponse: (response: Response) => {
      if (response.status === 200) {
        window.dispatchEvent(new CustomEvent('tasks-updated'));
      }
    },
    onFinish: () => {
      window.dispatchEvent(new CustomEvent('tasks-updated'));
    }
  });

  const runtime = useChatRuntime(chat);

  const handleSend = (text: string) => {
    if (!text.trim()) return;
    // @ts-ignore
    chat.sendMessage({ text });
    setInputValue('');
  };

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <ThreadPrimitive.Root className="flex flex-col h-full bg-white">
        <ThreadPrimitive.Viewport className="flex-1 overflow-y-auto p-4 space-y-4">
          <ThreadPrimitive.Empty>
            <div className="flex flex-col items-center justify-center h-full text-center space-y-6 py-10">
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-gray-900">How can I help you today?</h3>
                <p className="text-sm text-gray-500">Choose a suggestion below or type your own message.</p>
              </div>
              <div className="grid grid-cols-1 gap-2 w-full max-w-sm">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(s.prompt)}
                    className="text-left px-4 py-3 text-sm border border-gray-200 rounded-xl hover:bg-blue-50 hover:border-blue-200 transition-all text-gray-700 font-medium shadow-sm"
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

        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="relative flex items-end gap-2 bg-white border border-gray-300 rounded-xl px-3 py-2 shadow-sm focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(inputValue);
                }
              }}
              placeholder="Type a message..."
              className="flex-1 bg-transparent border-none focus:ring-0 resize-none py-1 text-sm min-h-[24px] max-h-[120px]"
              rows={1}
            />
            <button
              onClick={() => handleSend(inputValue)}
              disabled={!inputValue.trim() || chat.status === 'submitted' || chat.status === 'streaming'}
              className="p-1.5 rounded-lg bg-blue-600 text-white disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </div>
        </div>
      </ThreadPrimitive.Root>
    </AssistantRuntimeProvider>
  );
}
