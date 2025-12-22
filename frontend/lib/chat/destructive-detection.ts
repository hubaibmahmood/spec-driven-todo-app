// Detect destructive operations and provide confirmation
// Spec: 009-frontend-chat-integration - Phase 9 (T104-T105)

export interface DestructiveOperationInfo {
  isDestructive: boolean;
  operationType?: 'delete' | 'clear' | 'remove' | 'purge';
  scope?: 'all' | 'multiple' | 'bulk';
  confirmationMessage?: string;
  estimatedAffected?: string;
}

// Patterns that indicate destructive operations
const DESTRUCTIVE_PATTERNS = [
  // Delete all/everything
  { pattern: /delete\s+(all|every|everything)/i, type: 'delete', scope: 'all' },
  { pattern: /remove\s+(all|every|everything)/i, type: 'remove', scope: 'all' },
  { pattern: /clear\s+(all|every|everything)/i, type: 'clear', scope: 'all' },

  // Delete multiple/bulk
  { pattern: /delete\s+(multiple|many|bulk|several)/i, type: 'delete', scope: 'bulk' },
  { pattern: /remove\s+(multiple|many|bulk|several)/i, type: 'remove', scope: 'bulk' },

  // Delete with category (all completed, all old, etc.)
  { pattern: /delete\s+all\s+(completed|finished|done|old|past)/i, type: 'delete', scope: 'multiple' },
  { pattern: /remove\s+all\s+(completed|finished|done|old|past)/i, type: 'remove', scope: 'multiple' },
  { pattern: /clear\s+(completed|finished|done)/i, type: 'clear', scope: 'multiple' },

  // Purge operations
  { pattern: /purge/i, type: 'purge', scope: 'all' },

  // Drop/wipe operations
  { pattern: /(drop|wipe)\s+(all|everything)/i, type: 'delete', scope: 'all' },
];

/**
 * Detect if a user message contains a destructive operation
 * @param message - User's chat message
 * @returns Information about the destructive operation, if detected
 */
export function detectDestructiveOperation(message: string): DestructiveOperationInfo {
  const normalized = message.trim();

  for (const { pattern, type, scope } of DESTRUCTIVE_PATTERNS) {
    if (pattern.test(normalized)) {
      return {
        isDestructive: true,
        operationType: type as 'delete' | 'clear' | 'remove' | 'purge',
        scope: scope as 'all' | 'multiple' | 'bulk',
        confirmationMessage: generateConfirmationMessage(type, scope, normalized),
        estimatedAffected: estimateAffectedTasks(normalized),
      };
    }
  }

  return { isDestructive: false };
}

/**
 * Generate a confirmation message based on the operation
 * @param type - Type of destructive operation
 * @param scope - Scope of the operation
 * @param originalMessage - Original user message
 * @returns Confirmation message to display
 */
function generateConfirmationMessage(type: string, scope: string, originalMessage: string): string {
  const action = type === 'purge' ? 'permanently delete' : type;

  if (scope === 'all') {
    return `Are you sure you want to ${action} ALL tasks? This action cannot be undone.`;
  }

  if (scope === 'bulk' || scope === 'multiple') {
    // Try to extract the category from the message
    const categoryMatch = originalMessage.match(/(completed|finished|done|old|past|high|low)/i);
    const category = categoryMatch ? categoryMatch[1].toLowerCase() : 'multiple';

    return `Are you sure you want to ${action} ${category} tasks? This will affect multiple items and cannot be undone.`;
  }

  return `Are you sure you want to ${action} these tasks? This action cannot be undone.`;
}

/**
 * Estimate the number or type of tasks that will be affected
 * @param message - User's chat message
 * @returns Description of estimated affected tasks
 */
function estimateAffectedTasks(message: string): string {
  if (/\ball\b/i.test(message)) {
    return 'All tasks in your list';
  }

  if (/completed|finished|done/i.test(message)) {
    return 'All completed tasks';
  }

  if (/old|past/i.test(message)) {
    return 'All old or past tasks';
  }

  if (/high\s+priority/i.test(message)) {
    return 'All high priority tasks';
  }

  if (/low\s+priority/i.test(message)) {
    return 'All low priority tasks';
  }

  return 'Multiple tasks';
}
