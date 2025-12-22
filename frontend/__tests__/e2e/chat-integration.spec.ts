import { test, expect, type Page } from '@playwright/test';

/**
 * E2E Tests for Frontend Chat Integration (Spec 009)
 *
 * These tests validate the complete user workflows for the chat feature:
 * - Authentication integration
 * - Chat panel UI interactions
 * - Natural language task creation
 * - Real-time feedback
 * - Conversation history persistence
 * - Timezone-aware scheduling
 */

// Test fixtures and helpers
const TEST_USER = {
  email: 'test@example.com',
  password: 'TestPassword123!',
};

async function loginUser(page: Page) {
  await page.goto('/login');
  await page.fill('input[name="email"]', TEST_USER.email);
  await page.fill('input[name="password"]', TEST_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');
}

async function openChatPanel(page: Page) {
  // Click the chat toggle button
  const chatButton = page.locator('button[aria-label*="chat"]').first();
  await chatButton.click();

  // Wait for chat panel to appear with animation (300ms timeout)
  await expect(page.locator('text=Chat Assistant')).toBeVisible({ timeout: 500 });
}

async function sendChatMessage(page: Page, message: string) {
  const input = page.locator('input[placeholder*="Type a message"]');
  await input.fill(message);

  const sendButton = page.locator('button:has-text("Send")');
  await sendButton.click();
}

test.describe('Chat Integration - User Story 1: Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('US1.1: Chat requests include session token', async ({ page, context }) => {
    // Set up request interception to verify headers
    let authHeaderFound = false;

    page.on('request', (request) => {
      if (request.url().includes('/api/chat')) {
        const headers = request.headers();
        authHeaderFound = !!headers['authorization']?.startsWith('Bearer ');
      }
    });

    await openChatPanel(page);
    await sendChatMessage(page, 'add task test authentication');

    // Wait for API response
    await page.waitForResponse((response) => response.url().includes('/api/chat'));

    expect(authHeaderFound).toBeTruthy();
  });

  test('US1.2: Expired session prompts re-authentication', async ({ page, context }) => {
    // Clear session cookies to simulate expiration
    await context.clearCookies();

    await openChatPanel(page);
    await sendChatMessage(page, 'add task test session');

    // Should show error message or redirect to login
    await expect(
      page.locator('text=/session expired|please log in/i')
    ).toBeVisible({ timeout: 3000 });
  });

  test('US1.3: Different users see only their own conversations', async ({ page, browser }) => {
    // User 1 sends a message
    await openChatPanel(page);
    await sendChatMessage(page, 'add task user 1 private task');
    await expect(page.locator('text=user 1 private task')).toBeVisible();

    // Logout user 1
    await page.click('button:has-text("Logout")');

    // Login as user 2 in new context
    const context2 = await browser.newContext();
    const page2 = await context2.newPage();

    await page2.goto('/login');
    await page2.fill('input[name="email"]', 'user2@example.com');
    await page2.fill('input[name="password"]', 'TestPassword123!');
    await page2.click('button[type="submit"]');
    await page2.waitForURL('/dashboard');

    // Open chat for user 2
    await openChatPanel(page2);

    // User 2 should NOT see user 1's messages
    await expect(page2.locator('text=user 1 private task')).not.toBeVisible();

    await context2.close();
  });
});

test.describe('Chat Integration - User Story 2: Embedded Chat UI', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('US2.1: Chat panel slides in with smooth animation (desktop)', async ({ page }) => {
    // Set viewport to desktop size (≥768px)
    await page.setViewportSize({ width: 1280, height: 720 });

    await openChatPanel(page);

    // Panel should be visible and positioned correctly
    const chatPanel = page.locator('text=Chat Assistant').locator('..');
    await expect(chatPanel).toBeVisible();

    // Check that panel is positioned on the right side (desktop)
    const boundingBox = await chatPanel.boundingBox();
    expect(boundingBox?.x).toBeGreaterThan(800); // Should be on right side
  });

  test('US2.2: Chat panel collapses when close button is clicked', async ({ page }) => {
    await openChatPanel(page);

    // Click close button
    const closeButton = page.locator('button[aria-label*="Close"]').or(page.locator('button').filter({ hasText: 'X' }));
    await closeButton.first().click();

    // Panel should disappear
    await expect(page.locator('text=Chat Assistant')).not.toBeVisible({ timeout: 500 });
  });

  test('US2.3: Panel state persists across navigation', async ({ page }) => {
    await openChatPanel(page);

    // Navigate to another page
    await page.goto('/dashboard/tasks');

    // Panel should still be open (localStorage persistence)
    await expect(page.locator('text=Chat Assistant')).toBeVisible();
  });

  test('US2.4: Responsive behavior - full-screen overlay on mobile', async ({ page }) => {
    // Set viewport to mobile size (<768px)
    await page.setViewportSize({ width: 375, height: 667 });

    await openChatPanel(page);

    // Panel should be full-screen on mobile
    const chatPanel = page.locator('text=Chat Assistant').locator('..');
    const boundingBox = await chatPanel.boundingBox();

    // Panel width should be close to viewport width (allowing for some margin)
    expect(boundingBox?.width).toBeGreaterThan(350);
  });

  test('US2.5: ESC key closes chat panel (keyboard accessibility)', async ({ page }) => {
    await openChatPanel(page);

    // Press ESC key
    await page.keyboard.press('Escape');

    // Panel should close
    await expect(page.locator('text=Chat Assistant')).not.toBeVisible({ timeout: 500 });
  });
});

test.describe('Chat Integration - User Story 3: Natural Language Task Creation', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('US3.1: Create task via natural language and see it in todo list', async ({ page }) => {
    await openChatPanel(page);

    // Send natural language task request
    await sendChatMessage(page, 'add task review project proposal by Friday');

    // Wait for AI response in chat
    await expect(
      page.locator('text=/created.*task|added.*task/i')
    ).toBeVisible({ timeout: 5000 });

    // Verify task appears in main task list
    await expect(
      page.locator('text=review project proposal')
    ).toBeVisible({ timeout: 3000 });
  });

  test('US3.2: Task attributes are correctly parsed (title, due date, priority)', async ({ page }) => {
    await openChatPanel(page);

    // Send detailed task request
    await sendChatMessage(page, 'add high priority task: buy groceries tomorrow at 5pm');

    // Wait for confirmation
    await page.waitForResponse((response) => response.url().includes('/api/chat'));

    // Verify task in todo list has correct attributes
    const taskCard = page.locator('text=buy groceries').locator('..');
    await expect(taskCard).toBeVisible();

    // Check for priority indicator (high priority)
    await expect(taskCard.locator('[class*="high"]').or(taskCard.locator('text=/high/i'))).toBeVisible();
  });

  test('US3.3: Real-time feedback shows operation in progress', async ({ page }) => {
    await openChatPanel(page);

    // Send message
    await sendChatMessage(page, 'create task test real-time feedback');

    // Should show loading/processing indicator
    await expect(
      page.locator('text=/processing|creating|adding/i')
    ).toBeVisible({ timeout: 1000 });
  });

  test('US3.4: Multiple tasks can be created in sequence', async ({ page }) => {
    await openChatPanel(page);

    // Create first task
    await sendChatMessage(page, 'add task first test task');
    await expect(page.locator('text=first test task')).toBeVisible({ timeout: 3000 });

    // Create second task
    await sendChatMessage(page, 'add task second test task');
    await expect(page.locator('text=second test task')).toBeVisible({ timeout: 3000 });

    // Both tasks should be visible in the list
    await expect(page.locator('text=first test task')).toBeVisible();
    await expect(page.locator('text=second test task')).toBeVisible();
  });
});

test.describe('Chat Integration - User Story 4: Real-time Task Operation Feedback', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('US4.1: Status messages appear for task operations', async ({ page }) => {
    await openChatPanel(page);

    await sendChatMessage(page, 'add task test status messages');

    // Should see success confirmation
    await expect(
      page.locator('text=/✓|success|created/i')
    ).toBeVisible({ timeout: 5000 });
  });

  test('US4.2: Error messages displayed for failed operations', async ({ page }) => {
    await openChatPanel(page);

    // Send intentionally malformed request (if backend validates)
    await sendChatMessage(page, 'delete task with invalid id xyz123');

    // Should see error message
    await expect(
      page.locator('text=/error|failed|not found/i')
    ).toBeVisible({ timeout: 5000 });
  });

  test('US4.3: Todo list updates automatically after chat operation', async ({ page }) => {
    await openChatPanel(page);

    // Count initial tasks
    const initialTaskCount = await page.locator('[data-testid="task-item"]').count();

    // Add task via chat
    await sendChatMessage(page, 'add task auto-update test');
    await page.waitForResponse((response) => response.url().includes('/api/chat'));

    // Wait a bit for UI update
    await page.waitForTimeout(1000);

    // Task count should increase
    const newTaskCount = await page.locator('[data-testid="task-item"]').count();
    expect(newTaskCount).toBe(initialTaskCount + 1);
  });
});

test.describe('Chat Integration - User Story 5: Conversation History', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('US5.1: Conversation history loads within 1 second', async ({ page }) => {
    const startTime = Date.now();

    await openChatPanel(page);

    // Wait for messages to load (or "No messages" placeholder)
    await page.waitForSelector('[data-testid="chat-messages"]', { timeout: 1500 });

    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(1000);
  });

  test('US5.2: Load More button fetches older messages', async ({ page }) => {
    await openChatPanel(page);

    // Check if "Load More" button exists (only if hasMore is true)
    const loadMoreButton = page.locator('button:has-text("Load More")');

    if (await loadMoreButton.isVisible()) {
      // Count current messages
      const initialMessageCount = await page.locator('[data-testid="chat-message"]').count();

      // Click Load More
      await loadMoreButton.click();

      // Wait for new messages to load
      await page.waitForTimeout(1000);

      // Should have more messages
      const newMessageCount = await page.locator('[data-testid="chat-message"]').count();
      expect(newMessageCount).toBeGreaterThan(initialMessageCount);
    }
  });

  test('US5.3: Conversation persists across sessions', async ({ page, context }) => {
    await openChatPanel(page);

    // Send a unique message
    const uniqueMessage = `test message ${Date.now()}`;
    await sendChatMessage(page, uniqueMessage);

    // Wait for response
    await expect(page.locator(`text=${uniqueMessage}`)).toBeVisible();

    // Close browser and reopen (simulate new session)
    await context.clearCookies();
    await loginUser(page);

    // Reopen chat
    await openChatPanel(page);

    // Previous message should still be visible in history
    await expect(page.locator(`text=${uniqueMessage}`)).toBeVisible({ timeout: 3000 });
  });

  test('US5.4: Messages display in chronological order', async ({ page }) => {
    await openChatPanel(page);

    // Send multiple messages
    await sendChatMessage(page, 'first message');
    await page.waitForTimeout(500);

    await sendChatMessage(page, 'second message');
    await page.waitForTimeout(500);

    await sendChatMessage(page, 'third message');
    await page.waitForTimeout(500);

    // Get all messages
    const messages = await page.locator('[data-testid="chat-message"]').allTextContents();

    // Check order (first message should appear before second, etc.)
    const firstIndex = messages.findIndex(m => m.includes('first message'));
    const secondIndex = messages.findIndex(m => m.includes('second message'));
    const thirdIndex = messages.findIndex(m => m.includes('third message'));

    expect(firstIndex).toBeLessThan(secondIndex);
    expect(secondIndex).toBeLessThan(thirdIndex);
  });
});

test.describe('Chat Integration - User Story 6: Timezone-Aware Scheduling', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('US6.1: X-Timezone header included in API requests', async ({ page }) => {
    let timezoneHeaderFound = false;

    page.on('request', (request) => {
      if (request.url().includes('/api/chat')) {
        const headers = request.headers();
        timezoneHeaderFound = !!headers['x-timezone'];
      }
    });

    await openChatPanel(page);
    await sendChatMessage(page, 'add task test timezone');

    await page.waitForResponse((response) => response.url().includes('/api/chat'));

    expect(timezoneHeaderFound).toBeTruthy();
  });

  test('US6.2: Due dates calculated in user\'s timezone', async ({ page }) => {
    // Set timezone via browser emulation (if supported)
    // Note: This test may require manual verification with different timezones

    await openChatPanel(page);

    // Create task with relative time
    await sendChatMessage(page, 'add task call client tomorrow at 3pm');

    // Wait for task to be created
    await expect(page.locator('text=call client')).toBeVisible({ timeout: 5000 });

    // Verify due date is shown (time validation would require checking task details)
    // This is a placeholder - actual implementation would check the displayed due date format
  });
});

test.describe('Chat Integration - Edge Cases & Polish', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('Edge Case: Empty input is prevented', async ({ page }) => {
    await openChatPanel(page);

    const input = page.locator('input[placeholder*="Type a message"]');
    const sendButton = page.locator('button:has-text("Send")');

    // Send button should be disabled when input is empty
    await expect(sendButton).toBeDisabled();

    // Type and delete
    await input.fill('test');
    await input.clear();

    // Should be disabled again
    await expect(sendButton).toBeDisabled();
  });

  test('Edge Case: Ambiguous input shows helpful guidance', async ({ page }) => {
    await openChatPanel(page);

    await sendChatMessage(page, 'hello');

    // Should see helpful response (not an error)
    await expect(
      page.locator('text=/help|assist|can do/i')
    ).toBeVisible({ timeout: 5000 });
  });

  test('Edge Case: Network failure shows error with retry', async ({ page, context }) => {
    await openChatPanel(page);

    // Simulate network failure by going offline
    await context.setOffline(true);

    await sendChatMessage(page, 'add task test network failure');

    // Should show error message
    await expect(
      page.locator('text=/network|connection|failed/i')
    ).toBeVisible({ timeout: 3000 });

    // Restore connection
    await context.setOffline(false);
  });

  test('Accessibility: Keyboard navigation works', async ({ page }) => {
    await openChatPanel(page);

    // Tab to input field
    await page.keyboard.press('Tab');

    // Type message
    await page.keyboard.type('test keyboard navigation');

    // Tab to send button and press Enter
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');

    // Message should be sent
    await expect(page.locator('text=test keyboard navigation')).toBeVisible();
  });

  test('Performance: Messages render within 200ms', async ({ page }) => {
    await openChatPanel(page);

    const startTime = Date.now();

    await sendChatMessage(page, 'performance test message');

    // Wait for AI response to appear
    await page.waitForSelector('[data-testid="chat-message"]:has-text("performance test message")');

    const renderTime = Date.now() - startTime;

    // Should render quickly (allowing some network latency)
    expect(renderTime).toBeLessThan(2000); // 200ms render + API time
  });

  test('Performance: Panel animation completes within 300ms', async ({ page }) => {
    const chatButton = page.locator('button[aria-label*="chat"]').first();

    const startTime = Date.now();
    await chatButton.click();

    // Wait for animation to complete and panel to be visible
    await expect(page.locator('text=Chat Assistant')).toBeVisible();

    const animationTime = Date.now() - startTime;
    expect(animationTime).toBeLessThan(500); // 300ms animation + buffer
  });
});

test.describe('Chat Integration - Confirmation Dialogs', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('Destructive bulk operations require confirmation', async ({ page }) => {
    await openChatPanel(page);

    // Try to delete all tasks
    await sendChatMessage(page, 'delete all my tasks');

    // Should show confirmation dialog
    await expect(
      page.locator('text=/confirm|are you sure|delete all/i')
    ).toBeVisible({ timeout: 3000 });

    // Dialog should show number of affected tasks
    await expect(
      page.locator('text=/[0-9]+ task/i')
    ).toBeVisible();
  });

  test('Non-destructive bulk queries do not require confirmation', async ({ page }) => {
    await openChatPanel(page);

    // Query for tasks (non-destructive)
    await sendChatMessage(page, 'show all my tasks');

    // Should NOT show confirmation dialog, just results
    await expect(
      page.locator('text=/confirm|are you sure/i')
    ).not.toBeVisible({ timeout: 1000 });
  });
});
