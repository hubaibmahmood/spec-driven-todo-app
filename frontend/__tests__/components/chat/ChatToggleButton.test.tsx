// Component test for ChatToggleButton (TDD - Test First)
// Spec: 009-frontend-chat-integration - User Story 1

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatToggleButton from '@/components/chat/ChatToggleButton';

describe('ChatToggleButton', () => {
  it('should render a button with accessible label', () => {
    const mockOnClick = jest.fn();
    render(<ChatToggleButton onClick={mockOnClick} />);

    const button = screen.getByRole('button', { name: /chat/i });
    expect(button).toBeInTheDocument();
  });

  it('should have proper aria-label for screen readers', () => {
    const mockOnClick = jest.fn();
    render(<ChatToggleButton onClick={mockOnClick} />);

    const button = screen.getByLabelText(/toggle chat/i);
    expect(button).toBeInTheDocument();
  });

  it('should call onClick handler when clicked', async () => {
    const mockOnClick = jest.fn();
    const user = userEvent.setup();

    render(<ChatToggleButton onClick={mockOnClick} />);

    const button = screen.getByRole('button');
    await user.click(button);

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('should be keyboard accessible', async () => {
    const mockOnClick = jest.fn();
    const user = userEvent.setup();

    render(<ChatToggleButton onClick={mockOnClick} />);

    const button = screen.getByRole('button');
    button.focus();
    await user.keyboard('{Enter}');

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('should have fixed position styling for floating button', () => {
    const mockOnClick = jest.fn();
    const { container } = render(<ChatToggleButton onClick={mockOnClick} />);

    const button = container.querySelector('button');
    expect(button).toHaveClass('fixed');
  });
});
