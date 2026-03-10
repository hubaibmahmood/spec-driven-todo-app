'use client';

import { useVercelUseChatRuntime } from '@assistant-ui/react-ai-sdk';
import { useChat } from 'ai/react';
import { getAccessToken } from '@/lib/jwt-auth-client';
import { getUserTimezone } from '@/lib/utils/timezone';

export const useAssistantRuntime = () => {
  const accessToken = getAccessToken();
  const timezone = getUserTimezone();

  const chat = useChat({
    api: `${process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002'}/api/chat/stream`,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'X-Timezone': timezone,
    },
    // Map Vercel AI SDK roles to assistant-ui roles if necessary
    // Vercel AI SDK uses 'user' and 'assistant', which match assistant-ui
  });

  return useVercelUseChatRuntime(chat);
};
