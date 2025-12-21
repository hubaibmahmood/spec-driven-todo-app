// Component test for ChatPanel (TDD - Test First)
// Spec: 009-frontend-chat-integration - User Story 2 (T038)

import { render, screen, fireEvent } from '@testing-library/react';
import ChatPanel from '@/components/chat/ChatPanel';

// Mock useChat hook
jest.mock('@/hooks/useChat', () => ({
  useChat: () => ({
    isAuthenticated: true,
    sessionError: null,
    sendMessage: jest.fn(),
    loadHistory: jest.fn(),
    getOrCreateConversation: jest.fn(),
  }),
}));

describe('ChatPanel', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should not render when isOpen is false', () => {
    const { container } = render(<ChatPanel isOpen={false} onClose={mockOnClose} />);

    expect(container.firstChild).toBeNull();
  });

  it('should render when isOpen is true', () => {
    render(<ChatPanel isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByRole('dialog', { name: /chat panel/i })).toBeInTheDocument();
  });

  it('should display header with title', () => {
    render(<ChatPanel isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
  });

  it('should have close button in header', () => {
    render(<ChatPanel isOpen={true} onClose={mockOnClose} />);

    const closeButton = screen.getByRole('button', { name: /close chat panel/i });
    expect(closeButton).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', () => {
    render(<ChatPanel isOpen={true} onClose={mockOnClose} />);

    const closeButton = screen.getByRole('button', { name: /close chat panel/i });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should have responsive CSS classes for desktop (≥768px)', () => {
    const { container } = render(<ChatPanel isOpen={true} onClose={mockOnClose} />);

    const panel = container.querySelector('[role="dialog"]');
    expect(panel).toHaveClass('md:w-96'); // Desktop width
  });

  it('should have fixed position styling', () => {
    const { container } = render(<ChatPanel isOpen={true} onClose={mockOnClose} />);

    const panel = container.querySelector('[role="dialog"]');
    expect(panel).toHaveClass('fixed');
    expect(panel).toHaveClass('right-0');
  });

  it('should have transition animation classes', () => {
    const { container } = render(<ChatPanel isOpen={true} onClose={mockOnClose} />);

    const panel = container.querySelector('[role="dialog"]');
    expect(panel).toHaveClass('transition-transform');
    expect(panel).toHaveClass('duration-300');
  });

  it('should close panel when ESC key is pressed', () => {
    render(<ChatPanel isOpen={true} onClose={mockOnClose} />);

    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should have z-index for proper layering', () => {
    const { container } = render(<ChatPanel isOpen={true} onClose={mockOnClose} />);

    const panel = container.querySelector('[role="dialog"]');
    expect(panel).toHaveClass('z-40');
  });
});
