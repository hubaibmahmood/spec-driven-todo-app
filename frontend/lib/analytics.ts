// Google Analytics tracking utilities

declare global {
  interface Window {
    gtag?: (
      command: string,
      targetId: string,
      config?: Record<string, unknown>
    ) => void;
  }
}

// Track page views
export const pageview = (url: string) => {
  if (typeof window.gtag !== 'undefined') {
    window.gtag('config', process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID!, {
      page_path: url,
    });
  }
};

// Track custom events
export const event = ({
  action,
  category,
  label,
  value,
}: {
  action: string;
  category: string;
  label?: string;
  value?: number;
}) => {
  if (typeof window.gtag !== 'undefined') {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
    });
  }
};

// Example custom events for your todo app
export const trackTodoCreated = () => {
  event({
    action: 'todo_created',
    category: 'engagement',
    label: 'User created a new todo',
  });
};

export const trackTodoCompleted = () => {
  event({
    action: 'todo_completed',
    category: 'engagement',
    label: 'User completed a todo',
  });
};

export const trackTodoDeleted = () => {
  event({
    action: 'todo_deleted',
    category: 'engagement',
    label: 'User deleted a todo',
  });
};

export const trackUserSignup = () => {
  event({
    action: 'sign_up',
    category: 'conversion',
    label: 'User signed up',
  });
};

export const trackUserLogin = () => {
  event({
    action: 'login',
    category: 'conversion',
    label: 'User logged in',
  });
};
