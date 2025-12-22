// Component test for ChatMessage (TDD - Test First)
// Spec: 009-frontend-chat-integration - User Story 2

import { render, screen } from '@testing-library/react';
import ChatMessage from '@/components/chat/ChatMessage';
import type { Message } from '@/types/chat';

describe('ChatMessage', () => {
  const mockUserMessage: Message = {
    id: '1',
    conversationId: 'conv-1',
    content: 'Hello, AI assistant!',
    role: 'user',
    timestamp: new Date('2025-12-21T14:00:00Z'),
  };

  const mockAssistantMessage: Message = {
    id: '2',
    conversationId: 'conv-1',
    content: 'Hello! How can I help you today?',
    role: 'assistant',
    timestamp: new Date('2025-12-21T14:00:05Z'),
  };

  it('should render user message with correct content', () => {
    render(<ChatMessage message={mockUserMessage} />);

    expect(screen.getByText('Hello, AI assistant!')).toBeInTheDocument();
  });

  it('should render assistant message with correct content', () => {
    render(<ChatMessage message={mockAssistantMessage} />);

    expect(screen.getByText('Hello! How can I help you today?')).toBeInTheDocument();
  });

  it('should display formatted timestamp', () => {
    render(<ChatMessage message={mockUserMessage} />);

    // Should show time in some readable format (not raw ISO string)
    expect(screen.queryByText('2025-12-21T14:00:00Z')).not.toBeInTheDocument();
    // Should have some timestamp text present
    expect(screen.getByText(/:/)).toBeInTheDocument(); // Time format includes ":"
  });

  it('should apply different styling for user vs assistant messages', () => {
    const { container: userContainer } = render(<ChatMessage message={mockUserMessage} />);
    const { container: assistantContainer } = render(
      <ChatMessage message={mockAssistantMessage} />
    );

    const userMessageEl = userContainer.querySelector('[data-role="user"]');
    const assistantMessageEl = assistantContainer.querySelector('[data-role="assistant"]');

    expect(userMessageEl).toBeInTheDocument();
    expect(assistantMessageEl).toBeInTheDocument();
  });

  it('should display error message when operation fails', () => {
    const errorMessage: Message = {
      id: '3',
      conversationId: 'conv-1',
      content: 'Task operation failed',
      role: 'assistant',
      timestamp: new Date('2025-12-21T14:00:10Z'),
      metadata: {
        operation: 'create_task',
        status: 'error',
        errorMessage: 'Failed to create task: Invalid due date',
      },
    };

    render(<ChatMessage message={errorMessage} />);

    expect(screen.getByText(/Failed to create task: Invalid due date/i)).toBeInTheDocument();
  });

  it('should display success indicator for successful operations', () => {
    const successMessage: Message = {
      id: '4',
      conversationId: 'conv-1',
      content: 'Task created successfully',
      role: 'assistant',
      timestamp: new Date('2025-12-21T14:00:10Z'),
      metadata: {
        operation: 'create_task',
        taskId: 'task-123',
        status: 'success',
      },
    };

    render(<ChatMessage message={successMessage} />);

    // Should show success content
    expect(screen.getByText('Task created successfully')).toBeInTheDocument();
  });

  it('should handle long messages gracefully', () => {
    const longMessage: Message = {
      ...mockUserMessage,
      content: 'A'.repeat(1000), // 1000 character message
    };

    render(<ChatMessage message={longMessage} />);

    expect(screen.getByText('A'.repeat(1000))).toBeInTheDocument();
  });
});
