// Chat panel state management with localStorage persistence
// Spec: 009-frontend-chat-integration

'use client';

import { useState, useEffect } from 'react';
import { ChatPanelState } from '@/types/chat';

const STORAGE_KEY = 'chat-panel-state';

const defaultState: ChatPanelState = {
  isOpen: false,
  lastOpenedAt: undefined,
};

/**
 * Custom hook for managing chat panel state with localStorage persistence
 * @returns [state, setState] tuple for reading and updating panel state
 */
export function usePanelState(): [
  ChatPanelState,
  (newState: ChatPanelState) => void
] {
  const [state, setState] = useState<ChatPanelState>(defaultState);

  // Load saved state from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        setState(parsed);
      }
    } catch (error) {
      console.error('Failed to load chat panel state from localStorage:', error);
      // Fall back to default state if localStorage is corrupt
      setState(defaultState);
    }
  }, []);

  // Update state and persist to localStorage
  const updateState = (newState: ChatPanelState) => {
    try {
      setState(newState);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newState));
    } catch (error) {
      console.error('Failed to save chat panel state to localStorage:', error);
    }
  };

  return [state, updateState];
}
