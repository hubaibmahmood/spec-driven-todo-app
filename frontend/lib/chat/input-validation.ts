// Input validation and helpful guidance for chat messages
// Spec: 009-frontend-chat-integration - Phase 9 (T102)

export interface ValidationResult {
  isValid: boolean;
  guidance?: string;
  examples?: string[];
}

// Common greeting patterns
const GREETING_PATTERNS = [
  /^(hi|hello|hey|howdy|greetings?)$/i,
  /^(good\s+(morning|afternoon|evening))$/i,
  /^(what'?s?\s+up|sup)$/i,
];

// Unsupported operation patterns (operations outside task management)
const UNSUPPORTED_PATTERNS = [
  { pattern: /(send|write|compose)\s+(email|message|text|sms)/i, type: 'communication' },
  { pattern: /(call|phone|dial)\s+/i, type: 'communication' },
  { pattern: /(schedule|book|make)\s+(meeting|appointment|call|zoom)/i, type: 'calendar' },
  { pattern: /(set|create)\s+(alarm|timer|reminder)\s+for/i, type: 'device' },
  { pattern: /(play|pause|stop)\s+(music|song|video)/i, type: 'media' },
  { pattern: /(search|google|look up)\s+(for|on|about)/i, type: 'search' },
  { pattern: /(open|launch|start)\s+(app|application|program)/i, type: 'system' },
  { pattern: /(download|upload|transfer)\s+file/i, type: 'file' },
  { pattern: /^(order|buy|purchase|shop)\s+(me|for\s+me|online|now)/i, type: 'commerce' },
];

// Help request patterns
const HELP_PATTERNS = [
  /^(help|assist|support)$/i,
  /^(how\s+do\s+i|how\s+can\s+i|what\s+can\s+you)$/i,
  /^(commands?|options?)$/i,
];

// Too short or unclear patterns
const UNCLEAR_PATTERNS = [
  /^(ok|okay|yes|no|sure|thanks?|thank\s+you)$/i,
  /^[a-z]{1,2}$/i, // Single or two letter inputs
];

/**
 * Validate chat input and provide helpful guidance for ambiguous inputs
 * @param input - User's chat message
 * @returns Validation result with guidance if input is ambiguous
 */
export function validateChatInput(input: string): ValidationResult {
  const trimmed = input.trim();

  // Empty input
  if (!trimmed) {
    return {
      isValid: false,
      guidance: 'Please type a message to get started.',
      examples: [
        'Add a task to buy groceries tomorrow',
        'Show all my high priority tasks',
        'Mark the project proposal task as completed',
      ],
    };
  }

  // Too short (1-2 characters, excluding common valid inputs)
  if (trimmed.length <= 2 && !trimmed.match(/^\d+$/)) {
    return {
      isValid: false,
      guidance: 'Your message is too short. Please describe what you want to do with your tasks.',
      examples: [
        'Add a new task',
        'List my tasks',
        'Update a task',
      ],
    };
  }

  // Greetings
  if (GREETING_PATTERNS.some((pattern) => pattern.test(trimmed))) {
    return {
      isValid: false,
      guidance: 'Hello! I\'m here to help you manage your tasks. What would you like to do?',
      examples: [
        'Create a task for team meeting on Friday',
        'List all incomplete tasks',
        'Delete the old planning task',
      ],
    };
  }

  // Help requests
  if (HELP_PATTERNS.some((pattern) => pattern.test(trimmed))) {
    return {
      isValid: false,
      guidance: 'I can help you manage your tasks using natural language. Here are some things you can do:',
      examples: [
        'Add a task: "Create a task to review documentation by Friday"',
        'Update tasks: "Change all high priority tasks to next Monday"',
        'Complete tasks: "Mark the budget review task as done"',
        'List tasks: "Show me all my incomplete tasks"',
        'Delete tasks: "Delete all completed tasks"',
      ],
    };
  }

  // Unclear acknowledgments
  if (UNCLEAR_PATTERNS.some((pattern) => pattern.test(trimmed))) {
    return {
      isValid: false,
      guidance: 'I\'m not sure what you want me to do. Please describe a task operation.',
      examples: [
        'Add a reminder to call the client',
        'Update the meeting task to tomorrow',
        'Show my tasks for this week',
      ],
    };
  }

  // Unsupported operations (outside task management)
  for (const { pattern, type } of UNSUPPORTED_PATTERNS) {
    if (pattern.test(trimmed)) {
      return {
        isValid: false,
        guidance: getUnsupportedGuidance(type),
        examples: [
          'Add a task to prepare for the meeting',
          'Update task priority to high',
          'Mark tasks as completed',
          'Delete old tasks',
        ],
      };
    }
  }

  // Check if input is too long (max 5000 chars)
  if (trimmed.length > 5000) {
    return {
      isValid: false,
      guidance: 'Your message is too long. Please keep it under 5000 characters.',
    };
  }

  // Input looks valid
  return {
    isValid: true,
  };
}

/**
 * Get guidance message for unsupported operation types
 * @param type - Type of unsupported operation
 * @returns Guidance message explaining what's supported
 */
function getUnsupportedGuidance(type: string): string {
  switch (type) {
    case 'communication':
      return 'I can only help you manage tasks, not send messages or make calls. However, I can create tasks to remind you to do these things!';
    case 'calendar':
      return 'I can\'t directly schedule meetings, but I can create tasks with due dates to help you remember them.';
    case 'device':
      return 'I can\'t control device settings like alarms or timers, but I can create tasks as reminders.';
    case 'media':
      return 'I can\'t control media playback, but I\'m here to help you manage your task list!';
    case 'search':
      return 'I can\'t search the web, but I can help you manage tasks. Try asking me to add, update, or list your tasks.';
    case 'system':
      return 'I can\'t open apps or programs, but I can help you organize your tasks!';
    case 'file':
      return 'I can\'t handle file operations, but I can help you create tasks related to file management.';
    case 'commerce':
      return 'I can\'t make purchases, but I can create tasks to remind you to buy things!';
    default:
      return 'I\'m a task management assistant. I can help you create, update, list, and delete tasks.';
  }
}
