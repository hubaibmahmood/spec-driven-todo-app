'use client';

import { 
  Thread, 
  ThreadWelcome, 
  MessageList, 
  Composer, 
  AssistantRuntimeProvider,
  useAssistantRuntime
} from "@assistant-ui/react";
import { useVercelUseChatRuntime } from "@assistant-ui/react-ai-sdk";
import { useChat } from "ai/react";
import { getAccessToken } from "@/lib/jwt-auth-client";
import { getUserTimezone } from "@/lib/utils/timezone";
import MarkdownMessage from "./MarkdownMessage";

const MyThreadWelcome = () => {
  return (
    <ThreadWelcome
      message="How can I help you manage your tasks today?"
      suggestions={[
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
      ]}
    />
  );
};

export function MyAssistant() {
  const accessToken = getAccessToken();
  const timezone = getUserTimezone();

  // Initialize Vercel AI SDK useChat
  const chat = useChat({
    api: `${process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002'}/api/chat/stream`,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'X-Timezone': timezone,
    },
    // Map conversation ID if available (optional for now)
    onResponse: (response) => {
      // Handle response if needed
      if (response.status === 200) {
        // Refresh tasks if operations were performed
        window.dispatchEvent(new CustomEvent('tasks-updated'));
      }
    },
    onFinish: (message) => {
        // Finalize task refresh
        window.dispatchEvent(new CustomEvent('tasks-updated'));
    }
  });

  const runtime = useVercelUseChatRuntime(chat);

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <Thread 
        welcomeComponent={MyThreadWelcome}
        components={{
            Message: ({ message }) => (
                <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
                    <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                        message.role === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                        {message.role === 'assistant' ? (
                            <MarkdownMessage content={message.content} />
                        ) : (
                            <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                        )}
                    </div>
                </div>
            )
        }}
      />
    </AssistantRuntimeProvider>
  );
}
