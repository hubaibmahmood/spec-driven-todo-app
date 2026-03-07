import { useState, useEffect, useCallback } from 'react';
import { Notification, NotificationListResponse } from '@/types/notification';
import { httpClient } from '@/lib/http-client';
import { ApiError } from '@/lib/http-client';

const API_URL = '/api/backend';
const POLL_INTERVAL_MS = 60_000;

export interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  refresh: () => Promise<void>;
}

export function useNotifications(): UseNotificationsReturn {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  const fetchNotifications = useCallback(async () => {
    try {
      const data = await httpClient.get<NotificationListResponse>(
        `${API_URL}/notifications/`
      );
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch (err) {
      // Silently ignore auth errors (user not logged in yet)
      if (!(err instanceof ApiError && err.status === 401)) {
        console.error('[useNotifications] Failed to fetch:', err);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial fetch + polling every 60 seconds
  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const markAsRead = useCallback(async (id: number) => {
    try {
      await httpClient.patch(`${API_URL}/notifications/${id}/read`, {});
      setNotifications(prev =>
        prev.map(n => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('[useNotifications] Failed to mark as read:', err);
    }
  }, []);

  const markAllAsRead = useCallback(async () => {
    try {
      await httpClient.post(`${API_URL}/notifications/read-all`, {});
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('[useNotifications] Failed to mark all as read:', err);
    }
  }, []);

  return {
    notifications,
    unreadCount,
    isLoading,
    markAsRead,
    markAllAsRead,
    refresh: fetchNotifications,
  };
}
