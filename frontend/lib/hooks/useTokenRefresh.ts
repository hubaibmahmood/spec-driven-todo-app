/**
 * useTokenRefresh Hook
 *
 * Provides cross-tab token refresh synchronization using BroadcastChannel.
 * Ensures only one tab refreshes the token at a time and all tabs receive the update.
 */

import { useEffect, useRef, useCallback } from 'react';
import { refreshAccessToken, storeAccessToken, getAccessToken } from '../jwt-auth-client';

const REFRESH_LOCK_KEY = 'token_refresh_lock';
const TOKEN_CHANNEL_NAME = 'token_refresh_channel';
const LOCK_EXPIRY_MS = 5000; // 5 seconds

interface TokenRefreshMessage {
  type: 'token_refreshed';
  accessToken: string;
  tabId: string;
}

interface RefreshLock {
  tabId: string;
  timestamp: number;
}

// Generate unique tab ID
const generateTabId = () => `tab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

export function useTokenRefresh() {
  const tabIdRef = useRef<string>(generateTabId());
  const channelRef = useRef<BroadcastChannel | null>(null);

  /**
   * Attempt to acquire the refresh lock
   * Returns true if lock acquired, false otherwise
   */
  const acquireLock = useCallback((): boolean => {
    const now = Date.now();
    const lockData = localStorage.getItem(REFRESH_LOCK_KEY);

    // Check if there's an existing lock
    if (lockData) {
      try {
        const lock: RefreshLock = JSON.parse(lockData);

        // Check if lock is still valid (not expired)
        if (now - lock.timestamp < LOCK_EXPIRY_MS) {
          // Lock is held by another tab
          return false;
        }
        // Lock has expired, we can take it
      } catch (e) {
        // Invalid lock data, we can take it
      }
    }

    // Acquire the lock
    const newLock: RefreshLock = {
      tabId: tabIdRef.current,
      timestamp: now,
    };
    localStorage.setItem(REFRESH_LOCK_KEY, JSON.stringify(newLock));
    return true;
  }, []);

  /**
   * Release the refresh lock
   */
  const releaseLock = useCallback((): void => {
    const lockData = localStorage.getItem(REFRESH_LOCK_KEY);
    if (lockData) {
      try {
        const lock: RefreshLock = JSON.parse(lockData);
        // Only release if this tab owns the lock
        if (lock.tabId === tabIdRef.current) {
          localStorage.removeItem(REFRESH_LOCK_KEY);
        }
      } catch (e) {
        // Invalid lock data, remove it anyway
        localStorage.removeItem(REFRESH_LOCK_KEY);
      }
    }
  }, []);

  /**
   * Broadcast token to all tabs via BroadcastChannel
   */
  const broadcastToken = useCallback((accessToken: string): void => {
    if (channelRef.current) {
      const message: TokenRefreshMessage = {
        type: 'token_refreshed',
        accessToken,
        tabId: tabIdRef.current,
      };
      channelRef.current.postMessage(message);
    }
  }, []);

  /**
   * Main refresh function with cross-tab coordination
   */
  const refreshToken = useCallback(async (): Promise<string | null> => {
    // Try to acquire lock
    if (!acquireLock()) {
      // Another tab is refreshing, wait for broadcast
      return null;
    }

    try {
      // Perform refresh
      const newAccessToken = await refreshAccessToken();

      // Broadcast to all tabs
      broadcastToken(newAccessToken);

      return newAccessToken;
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw error;
    } finally {
      // Always release the lock
      releaseLock();
    }
  }, [acquireLock, releaseLock, broadcastToken]);

  /**
   * Initialize BroadcastChannel and listeners
   */
  useEffect(() => {
    // Initialize BroadcastChannel if supported
    if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
      channelRef.current = new BroadcastChannel(TOKEN_CHANNEL_NAME);

      // Listen for token updates from other tabs
      channelRef.current.onmessage = (event: MessageEvent<TokenRefreshMessage>) => {
        const { type, accessToken, tabId } = event.data;

        // Ignore messages from this tab
        if (tabId === tabIdRef.current) {
          return;
        }

        // Update token when another tab refreshes
        if (type === 'token_refreshed' && accessToken) {
          storeAccessToken(accessToken);
        }
      };
    }

    // Fallback: localStorage event listener for browsers without BroadcastChannel
    const handleStorageEvent = (e: StorageEvent) => {
      // Listen for token changes from other tabs
      if (e.key === 'jwt_access_token' && e.newValue) {
        // Token was updated by another tab
        // No action needed as localStorage is already updated
        // This is just for debugging/logging
        console.log('Token updated by another tab via localStorage');
      }
    };

    window.addEventListener('storage', handleStorageEvent);

    // Cleanup
    return () => {
      if (channelRef.current) {
        channelRef.current.close();
        channelRef.current = null;
      }
      window.removeEventListener('storage', handleStorageEvent);
      releaseLock(); // Release lock if tab closes
    };
  }, [releaseLock]);

  return {
    refreshToken,
    tabId: tabIdRef.current,
  };
}
