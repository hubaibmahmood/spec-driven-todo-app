'use client';

import { useChatRuntime } from '@assistant-ui/react-ai-sdk';
import { useChat } from '@ai-sdk/react';
import { getAccessToken } from '@/lib/jwt-auth-client';
import { getUserTimezone } from '@/lib/utils/timezone';

export const useAssistantRuntime = () => {
  const accessToken = getAccessToken();
  const timezone = getUserTimezone();

  const chat = useChat({
    // @ts-ignore
    api: `${process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002'}/api/chat/stream`,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'X-Timezone': timezone,
    },
  });

  return useChatRuntime(chat);
};
