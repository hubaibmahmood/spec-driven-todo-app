export interface Notification {
  id: number;
  user_id: string;
  task_id: number | null;
  type: 'due_soon' | 'overdue';
  message: string;
  is_read: boolean;
  sent_email: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  unread_count: number;
}
