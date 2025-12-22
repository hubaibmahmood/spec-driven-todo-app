# Manual Testing Guide - Phase 9 Critical Edge Cases

**Feature:** Frontend Chat Integration - Phase 9 Edge Cases
**Date:** 2025-12-22
**Version:** 1.0

This guide covers manual testing procedures for the 5 critical edge cases implemented in Phase 9:
- T102: Handle empty/ambiguous input with helpful guidance
- T103: Session timeout handling mid-conversation
- T106-T107: Network failure retry logic with exponential backoff
- T104-T105: Confirmation dialog for destructive bulk operations
- T109: Handle unsupported operations gracefully

---

## Prerequisites

### 1. Start All Services

Open 4 terminal windows and run:

```bash
# Terminal 1 - Backend API
cd backend
source venv/bin/activate
uvicorn src.api.main:app --reload --port 8000

# Terminal 2 - Auth Server
cd auth-server
npm run dev

# Terminal 3 - AI Agent
cd ai-agent
source venv/bin/activate
python -m uvicorn src.ai_agent.main:app --reload --port 8002

# Terminal 4 - Frontend
cd frontend
npm run dev
```

### 2. Access Application

1. Open browser to `http://localhost:3000`
2. Log in with your credentials
3. Navigate to dashboard
4. Click the chat toggle button (bottom-right floating button)

---

## Test 1: Empty/Ambiguous Input (T102)

### Test Case 1.1: Empty Input

**Steps:**
1. Open chat panel
2. Try to send an empty message (just press Enter without typing)

**Expected Result:**
- Input is disabled (send button should be grayed out)
- No message sent
- Input remains empty

---

### Test Case 1.2: Greeting

**Steps:**
1. Type: `hello`
2. Press Enter

**Expected Result:**
- Blue guidance message appears with light blue background
- Content: "Hello! I'm here to help you manage your tasks. What would you like to do?"
- Shows 3 example commands in a list:
  - "Create a task for team meeting on Friday"
  - "List all incomplete tasks"
  - "Delete the old planning task"
- Input field is cleared automatically

**Screenshot Expected:**
```
┌─────────────────────────────────────────┐
│ [AI Assistant]                      [×] │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Hello! I'm here to help you...   │ │
│  │                                   │ │
│  │ Try these examples:               │ │
│  │ • "Create a task for..."          │ │
│  │ • "List all incomplete tasks"     │ │
│  │ • "Delete the old planning task"  │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Test Variations:**
- `hi` ✓
- `hey` ✓
- `good morning` ✓
- `good evening` ✓
- `what's up` ✓

---

### Test Case 1.3: Help Request

**Steps:**
1. Type: `help`
2. Press Enter

**Expected Result:**
- Blue guidance message appears
- Content: "I can help you manage your tasks using natural language. Here are some things you can do:"
- Shows 5 example commands:
  - Add a task: "Create a task to review documentation by Friday"
  - Update tasks: "Change all high priority tasks to next Monday"
  - Complete tasks: "Mark the budget review task as done"
  - List tasks: "Show me all my incomplete tasks"
  - Delete tasks: "Delete all completed tasks"

**Test Variations:**
- `how do i` ✓
- `how can i` ✓
- `what can you` ✓
- `commands` ✓

---

### Test Case 1.4: Unclear Input

**Steps:**
1. Type: `ok`
2. Press Enter

**Expected Result:**
- Blue guidance message: "I'm not sure what you want me to do. Please describe a task operation."
- Shows 3 examples:
  - "Add a reminder to call the client"
  - "Update the meeting task to tomorrow"
  - "Show my tasks for this week"

**Test Variations:**
- `yes` ✓
- `no` ✓
- `thanks` ✓
- `okay` ✓
- `sure` ✓

---

### Test Case 1.5: Too Short Input

**Steps:**
1. Type: `a` (single letter)
2. Press Enter

**Expected Result:**
- Guidance message: "Your message is too short. Please describe what you want to do with your tasks."
- Shows 3 examples:
  - "Add a new task"
  - "List my tasks"
  - "Update a task"

**Test Variations:**
- Any single letter: `b`, `c`, `x` ✓
- Two letters: `ab` ✓

---

## Test 2: Session Timeout Handling (T103)

### Test Case 2.1: Simulate Session Expiry

**Option A - Quick Test (Mock expired token):**

**Steps:**
1. Open browser DevTools (F12 or Right-click → Inspect)
2. Go to Application tab → Cookies → `http://localhost:3000`
3. Find the `better_auth.session_token` cookie
4. Double-click the value and change it to: `expired_token_12345`
5. Press Enter to save
6. In chat panel, type: `Add a task to test session timeout`
7. Press Enter

**Expected Result:**
- Yellow warning banner appears at bottom of chat (above input area)
- Warning icon (⚠️) displayed
- Title: "Session Expired"
- Message: "Your session has expired. Please log in again to continue. Your message will be sent automatically after login."
- Yellow "Log In Again" button
- Your typed message is preserved internally (not visible, but stored)
- Error banner stays visible

**Screenshot Expected:**
```
┌─────────────────────────────────────────┐
│ [Chat Messages Area]                    │
├─────────────────────────────────────────┤
│ ⚠️  Session Expired                     │
│    Your session has expired. Please     │
│    log in again to continue. Your       │
│    message will be sent automatically   │
│    after login.                         │
│    [Log In Again]                       │
├─────────────────────────────────────────┤
│ [Input Area]                            │
└─────────────────────────────────────────┘
```

**Option B - Wait for Natural Expiry (Longer Test):**
1. Leave the app open without interaction
2. Wait for session timeout duration (check auth-server config, usually 15-30 minutes)
3. Try to send a chat message

**Expected Result:**
- Same as Option A

---

### Test Case 2.2: Re-authentication Flow

**Steps:**
1. After session expires (from Test Case 2.1)
2. Click "Log In Again" button
3. You're redirected to login page
4. Enter credentials and log in
5. You're redirected back to dashboard

**Expected Result:**
- Chat panel opens automatically
- Session expired banner disappears
- Pending message is sent automatically (you'll see it in chat as user message)
- AI processes the message
- Response appears in chat
- Task appears in the task list (if it was a create task command)

**Timing:**
- Auto-retry happens within 1-2 seconds of landing on dashboard
- Should feel seamless to user

---

### Test Case 2.3: Session Timeout During Message Send

**Steps:**
1. Have a valid session
2. Open DevTools Network tab
3. Type a message but DON'T press Enter yet
4. In another tab, invalidate the session cookie (Application → Cookies)
5. Now press Enter in chat

**Expected Result:**
- Processing indicator shows briefly
- Then session expired banner appears
- Message is preserved for retry after login

---

## Test 3: Network Retry Logic (T106-T107)

### Test Case 3.1: Simulate Network Failure

**Option A - Stop AI Agent Service:**

**Steps:**
1. In Terminal 3 (AI Agent service), press `Ctrl+C` to stop the service
2. Verify it's stopped: `curl http://localhost:8002/health` (should fail)
3. In chat panel, type: `Add a task to test network retry`
4. Press Enter
5. Watch the behavior carefully - you'll see retry attempts with delays

**Expected Behavior Timeline:**
- **T+0s**: Processing indicator shows
- **T+1s**: First retry attempt (after 1 second delay)
- **T+3s**: Second retry attempt (after 2 second delay)
- **T+7s**: Third retry attempt (after 4 second delay)
- **T+8s**: All retries exhausted, error displays

**Expected Result After ~8 seconds:**
- Red error banner appears at bottom of chat
- Error icon (X in circle) displayed
- Error message: "Network request failed after 3 retries: Failed to send message: [error details]"
- Additional text: "Failed after 3 retry attempts."
- "Retry Message" button appears (red button)
- Processing indicator disappears
- Optimistic user message is removed from chat

**Screenshot Expected:**
```
┌─────────────────────────────────────────┐
│ [Chat Messages Area]                    │
├─────────────────────────────────────────┤
│ ❌  Network request failed after 3      │
│     retries: Failed to send message...  │
│     Failed after 3 retry attempts.      │
│     [Retry Message]                     │
├─────────────────────────────────────────┤
│ [Input Area]                            │
└─────────────────────────────────────────┘
```

**Option B - Throttle Network (Chrome DevTools):**

**Steps:**
1. Open DevTools (F12)
2. Go to Network tab
3. Find throttling dropdown (usually says "No throttling")
4. Select "Offline"
5. In chat, send a message
6. Watch retry behavior

**Expected Result:**
- Same as Option A
- Network tab shows failed requests turning red

**Option C - Use Firewall/Network Settings:**
- Block port 8002 temporarily
- Send message
- Observe retry behavior

---

### Test Case 3.2: Manual Retry After Network Recovery

**Steps:**
1. After network failure from Test Case 3.1
2. Restart AI Agent service:
   ```bash
   # In Terminal 3
   cd ai-agent
   python -m uvicorn src.ai_agent.main:app --reload --port 8002
   ```
3. Wait for service to start (look for "Uvicorn running on...")
4. Verify it's running: `curl http://localhost:8002/health`
5. In chat, click the "Retry Message" button

**Expected Result:**
- Button shows loading state briefly
- Message sends successfully on first attempt (no retries needed since network is good)
- Red error banner disappears
- User message appears in chat
- AI response appears
- Task appears in task list (if applicable)
- Retry count resets to 0

---

### Test Case 3.3: Successful Send (Verify No False Positives)

**Steps:**
1. Ensure all services are running and healthy
2. Type: `Add a task to buy milk tomorrow`
3. Press Enter
4. Observe timing

**Expected Result:**
- Message sends on first attempt (typically within 500ms-2s)
- No retry delays
- No retry count shown in any error
- Processing indicator shows briefly then disappears
- Response appears quickly
- Task appears in list

**Verification:**
- Open DevTools Network tab
- Look for POST request to `/api/chat`
- Should see only ONE request, not multiple retries
- Status should be 200 OK

---

### Test Case 3.4: Intermittent Network (Recovery During Retry)

**Steps:**
1. Stop AI Agent service
2. Send a message (retries will start)
3. After ~2 seconds (during retry cycle), restart AI Agent
4. Watch what happens

**Expected Result:**
- One of the retry attempts should succeed
- Message goes through
- No error shown
- Normal successful flow continues

---

## Test 4: Destructive Operation Confirmations (T104-T105)

### Test Case 4.1: Delete All Tasks

**Steps:**
1. Type: `delete all tasks`
2. Press Enter

**Expected Result:**
- Modal overlay appears (dark backdrop covering screen)
- Modal appears centered on screen with:
  - Red warning icon (⚠️ in red circle)
  - Title: "Confirm Destructive Operation"
  - Message: "Are you sure you want to delete ALL tasks? This action cannot be undone."
  - Yellow warning box below message:
    - Warning icon
    - Text: "This will affect:"
    - "All tasks in your list"
  - Two buttons at bottom:
    - "Cancel" (gray/white button on left)
    - "Yes, Proceed" (red button on right)
- Input field in chat still contains: `delete all tasks`
- Chat panel remains visible behind modal

**Screenshot Expected:**
```
┌─────────────────────────────────────────┐
│          [Modal - Centered]             │
│                                         │
│         🛑 (Red Circle Icon)            │
│                                         │
│    Confirm Destructive Operation        │
│                                         │
│  Are you sure you want to delete ALL    │
│  tasks? This action cannot be undone.   │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ ⚠️ This will affect:              │ │
│  │    All tasks in your list         │ │
│  └───────────────────────────────────┘ │
│                                         │
│    [Cancel]      [Yes, Proceed]        │
│                                         │
└─────────────────────────────────────────┘
```

---

### Test Case 4.2: Cancel Destructive Operation

**Steps:**
1. Trigger modal: Type `delete all tasks` and press Enter
2. Modal appears
3. Click "Cancel" button

**Expected Result:**
- Modal closes immediately (smooth fade out)
- Backdrop disappears
- Chat panel is fully visible again
- Input field STILL CONTAINS original text: `delete all tasks`
- No message sent to backend
- Tasks remain unchanged in list
- User can now edit the message or clear it

**Use Case:** User made a typo or changed their mind

---

### Test Case 4.3: Confirm Destructive Operation

**Preparation:**
1. Make sure you have some completed tasks in your list
2. Or create a few: "Add task: Test task 1", mark it complete, repeat

**Steps:**
1. Type: `delete all completed tasks`
2. Press Enter
3. Modal appears with message: "Are you sure you want to delete completed tasks?"
4. Estimated affected: "All completed tasks"
5. Click "Yes, Proceed" button

**Expected Result:**
- Modal closes immediately
- Message is sent to AI agent
- User message appears in chat: "delete all completed tasks"
- Processing indicator shows
- AI agent processes the request
- Assistant response appears (e.g., "I've deleted 3 completed tasks")
- Completed tasks are removed from task list
- Only incomplete tasks remain
- Task list refreshes automatically

---

### Test Case 4.4: Various Destructive Patterns

Test each of these inputs individually. Each should trigger the confirmation modal:

| Input Command | Expected Confirmation Message | Estimated Affected |
|---------------|------------------------------|-------------------|
| `delete all tasks` | "...delete ALL tasks?" | "All tasks in your list" |
| `remove all tasks` | "...remove ALL tasks?" | "All tasks in your list" |
| `clear everything` | "...clear ALL tasks?" | "All tasks in your list" |
| `delete all my tasks` | "...delete ALL tasks?" | "All tasks in your list" |
| `remove everything` | "...remove ALL tasks?" | "All tasks in your list" |
| `delete all old tasks` | "...delete old tasks?" | "All old or past tasks" |
| `remove all finished tasks` | "...remove finished tasks?" | "All completed tasks" |
| `delete all completed tasks` | "...delete completed tasks?" | "All completed tasks" |
| `clear completed` | "...clear completed tasks?" | "All completed tasks" |
| `delete all done tasks` | "...delete done tasks?" | "All completed tasks" |
| `purge tasks` | "...permanently delete ALL tasks?" | "All tasks in your list" |
| `delete all high priority tasks` | "...delete high tasks?" | "All high priority tasks" |
| `remove all low priority tasks` | "...remove low tasks?" | "All low priority tasks" |

**Test Process for Each:**
1. Type the command
2. Verify modal appears
3. Check message text matches expected pattern
4. Check "Estimated Affected" matches expected category
5. Click Cancel (don't actually delete)
6. Verify modal closes and input retained

---

### Test Case 4.5: Non-Destructive Operations (No Modal)

These commands should NOT trigger the confirmation modal:

| Input Command | Expected Behavior |
|---------------|------------------|
| `delete task number 5` | No modal - sends directly (single task) |
| `remove the meeting task` | No modal - sends directly (single task) |
| `add a task to delete files` | No modal - just creating a task |
| `update task priority` | No modal - update operation |
| `show all tasks` | No modal - read operation |
| `list completed tasks` | No modal - read operation |
| `mark task as complete` | No modal - single update |

**Verification:**
- Message sends immediately without confirmation
- No modal appears
- Normal chat flow continues

---

### Test Case 4.6: Modal Accessibility

**Keyboard Navigation:**

**Steps:**
1. Type: `delete all tasks`
2. Press Enter
3. Modal appears
4. Press Tab key multiple times
5. Press Enter when focused on Cancel
6. Repeat steps 1-3
7. Press Enter when focused on "Yes, Proceed"

**Expected Result:**
- Tab key moves focus between Cancel and Proceed buttons
- Focus indicator (ring) is visible
- Enter key activates focused button
- Escape key closes modal (if implemented)

**Screen Reader Test (Optional):**
1. Enable screen reader (VoiceOver on Mac, NVDA on Windows)
2. Trigger modal
3. Verify it announces: "Confirm Destructive Operation" dialog
4. Verify it reads the warning message
5. Verify buttons are properly labeled

---

## Test 5: Unsupported Operations (T109)

### Test Case 5.1: Communication Operations

**Test Case 5.1a: Email**

**Steps:**
1. Type: `send an email to john@example.com`
2. Press Enter

**Expected Result:**
- Blue guidance message appears (light blue background)
- Content: "I can only help you manage tasks, not send messages or make calls. However, I can create tasks to remind you to do these things!"
- Shows 4 task operation examples:
  - "Add a task to prepare for the meeting"
  - "Update task priority to high"
  - "Mark tasks as completed"
  - "Delete old tasks"
- Input is cleared

**Test Variations:**
- `write an email to the team` ✓
- `compose a message to my boss` ✓
- `send a text to mom` ✓
- `send sms to 555-1234` ✓

---

**Test Case 5.1b: Phone Calls**

**Steps:**
1. Type: `call my mom`
2. Press Enter

**Expected Result:**
- Guidance: "I can only help you manage tasks, not send messages or make calls. However, I can create tasks to remind you to do these things!"
- Shows task examples

**Test Variations:**
- `phone the office` ✓
- `dial 555-1234` ✓
- `call john` ✓

---

### Test Case 5.2: Calendar Operations

**Steps:**
1. Type: `schedule a meeting for tomorrow at 2pm`
2. Press Enter

**Expected Result:**
- Guidance: "I can't directly schedule meetings, but I can create tasks with due dates to help you remember them."
- Shows 4 task examples

**Test Variations:**
- `book an appointment with the dentist` ✓
- `make a meeting with the team` ✓
- `schedule a zoom call` ✓

---

### Test Case 5.3: Device Controls

**Steps:**
1. Type: `set an alarm for 8am`
2. Press Enter

**Expected Result:**
- Guidance: "I can't control device settings like alarms or timers, but I can create tasks as reminders."
- Shows task examples

**Test Variations:**
- `create a timer for 10 minutes` ✓
- `set a reminder for 5pm` (Note: might be ambiguous with task reminder) ✓

---

### Test Case 5.4: Media Controls

**Steps:**
1. Type: `play some music`
2. Press Enter

**Expected Result:**
- Guidance: "I can't control media playback, but I'm here to help you manage your task list!"
- Shows task examples

**Test Variations:**
- `pause the video` ✓
- `stop the song` ✓
- `play my playlist` ✓

---

### Test Case 5.5: Web Search

**Steps:**
1. Type: `search google for chocolate cake recipes`
2. Press Enter

**Expected Result:**
- Guidance: "I can't search the web, but I can help you manage tasks. Try asking me to add, update, or list your tasks."
- Shows task examples

**Test Variations:**
- `look up weather forecast` ✓
- `google the news` ✓
- `search for nearby restaurants` ✓

---

### Test Case 5.6: System Operations

**Steps:**
1. Type: `open Chrome`
2. Press Enter

**Expected Result:**
- Guidance: "I can't open apps or programs, but I can help you organize your tasks!"
- Shows task examples

**Test Variations:**
- `launch Spotify` ✓
- `start the calculator app` ✓
- `open my email application` ✓

---

### Test Case 5.7: File Operations

**Steps:**
1. Type: `download the report file`
2. Press Enter

**Expected Result:**
- Guidance: "I can't handle file operations, but I can help you create tasks related to file management."
- Shows task examples

**Test Variations:**
- `upload my resume` ✓
- `transfer files to USB` ✓
- `save this document` ✓

---

### Test Case 5.8: Commerce Operations

**Steps:**
1. Type: `order pizza`
2. Press Enter

**Expected Result:**
- Guidance: "I can't make purchases, but I can create tasks to remind you to buy things!"
- Shows task examples

**Test Variations:**
- `buy groceries online` ✓
- `purchase new shoes` ✓
- `shop for a gift` ✓

---

### Test Case 5.9: Supported Alternative Suggestions

After getting an unsupported operation error, test that the suggestions work:

**Steps:**
1. Get unsupported error: `send email to john`
2. Read the examples shown
3. Try one of the suggested commands: `Add a task to email John about the project`
4. Press Enter

**Expected Result:**
- Message sends successfully (no guidance, no error)
- Task is created
- Works as normal

---

## Test 6: Combined Scenarios (Integration Tests)

### Test Case 6.1: Session Timeout + Network Retry

**Steps:**
1. Invalidate session token (see Test 2.1)
2. Stop AI Agent service (see Test 3.1)
3. Type: `Add a task to test combined scenario`
4. Press Enter

**Expected Result:**
- Session expired banner appears first (401 detected immediately)
- Shows "Log In Again" button
- Click button, log in
- After login, auto-retry kicks in
- But network is still down, so retry logic activates
- After 3 retries (~8 seconds), shows network error
- Restart AI Agent
- Click "Retry Message"
- Message finally sends successfully

**Complexity:** High - tests interaction of two error handling systems

---

### Test Case 6.2: Ambiguous → Valid → Destructive Flow

**Steps:**
1. Type: `hello`
2. Press Enter - see guidance
3. Type: `delete all my tasks`
4. Press Enter - see confirmation modal
5. Click "Cancel"
6. Input still contains: `delete all my tasks`
7. Edit to: `Add a task to organize all my files`
8. Press Enter

**Expected Result:**
- Each step shows appropriate UI (guidance → modal → normal send)
- Final message creates task successfully
- Flow is smooth, no errors

---

### Test Case 6.3: Unsupported → Correct → Destructive

**Steps:**
1. Type: `send email to everyone about task cleanup`
2. Press Enter - see unsupported guidance
3. Type: `delete all tasks instead`
4. Press Enter - see destructive confirmation
5. Click "Yes, Proceed"

**Expected Result:**
- Guidance → Confirmation → Execution
- All transitions smooth
- Final operation executes

---

### Test Case 6.4: Network Error During Destructive Operation

**Steps:**
1. Stop AI Agent service
2. Type: `delete all completed tasks`
3. Press Enter
4. Confirmation modal appears
5. Click "Yes, Proceed"
6. Network retry logic kicks in

**Expected Result:**
- Modal closes
- Processing indicator shows
- Retries happen (3 attempts)
- Error appears after retries exhausted
- "Retry Message" button available
- Restart service and retry - should work

---

## Debugging Tips

### Check Frontend Console

Open DevTools → Console tab. Look for:
- Error messages
- Network errors
- Component warnings

### Check Network Tab

Open DevTools → Network tab:
- Filter by "Fetch/XHR"
- Look for `/api/chat` requests
- Check status codes (200, 401, 500, etc.)
- Inspect request/response payloads

### Check Backend Logs

Look at terminal windows for:
- AI Agent logs (Terminal 3)
- Backend API logs (Terminal 1)
- Auth server logs (Terminal 2)

### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| No guidance shows | Frontend error | Check console for React errors |
| Modal doesn't appear | CSS/rendering issue | Check if modal component loaded |
| Retry doesn't work | AI Agent never restarted | Verify service is running on port 8002 |
| Session timeout not triggering | Cookie not invalidated | Try harder refresh (Cmd+Shift+R) |
| Messages send immediately | Validation bypassed | Check if validation logic is running |

### Reset Test Environment

If tests are failing inconsistently:

```bash
# Clear browser data
# Chrome: Settings → Privacy → Clear browsing data → Cookies

# Restart all services
# Kill all terminals (Ctrl+C) and restart them

# Clear localStorage
# DevTools → Application → Local Storage → Clear All

# Hard refresh browser
# Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

---

## Testing Checklist

Print this section and check off as you complete tests:

### T102: Empty/Ambiguous Input
- [ ] Empty input prevented
- [ ] "hello" shows greeting guidance
- [ ] "help" shows command list
- [ ] "ok" shows unclear message guidance
- [ ] Single letter shows "too short" guidance
- [ ] All guidance messages have examples
- [ ] Blue styling applied correctly
- [ ] Input cleared after guidance

### T103: Session Timeout
- [ ] Invalid token triggers session expired banner
- [ ] Yellow warning style correct
- [ ] "Log In Again" button present
- [ ] Message preserved during logout
- [ ] Auto-retry after login works
- [ ] Banner disappears after successful retry

### T106-T107: Network Retry
- [ ] Network failure triggers retry
- [ ] 3 retry attempts occur
- [ ] Exponential backoff delays observed (1s, 2s, 4s)
- [ ] Error shows "Failed after 3 retries"
- [ ] "Retry Message" button appears
- [ ] Manual retry works after network recovery
- [ ] Successful messages don't trigger retry
- [ ] No false positive retries

### T104-T105: Destructive Confirmations
- [ ] "delete all" triggers modal
- [ ] "remove all" triggers modal
- [ ] "clear everything" triggers modal
- [ ] "purge" triggers modal
- [ ] Modal shows red warning icon
- [ ] Estimated affected tasks displayed
- [ ] Cancel preserves message in input
- [ ] Confirm executes operation
- [ ] Single task deletes don't trigger modal
- [ ] Read operations don't trigger modal

### T109: Unsupported Operations
- [ ] Email requests rejected with guidance
- [ ] Call requests rejected
- [ ] Meeting scheduling rejected
- [ ] Alarm/timer requests rejected
- [ ] Media control requests rejected
- [ ] Search requests rejected
- [ ] System operation requests rejected
- [ ] File operation requests rejected
- [ ] Commerce requests rejected
- [ ] All show helpful alternatives
- [ ] Suggested commands work correctly

### Integration Tests
- [ ] Session timeout + network retry works
- [ ] Multiple error types handled in sequence
- [ ] UI stays responsive during errors
- [ ] No memory leaks or performance issues
- [ ] All transitions smooth

---

## Test Results Template

Copy this template to record your test results:

```
Testing Session: [Date/Time]
Tester: [Your Name]
Environment: [Local Development]
Browser: [Chrome/Firefox/Safari] [Version]

T102 Results: ✅ Pass / ❌ Fail
Notes: ___________________________________

T103 Results: ✅ Pass / ❌ Fail
Notes: ___________________________________

T106-T107 Results: ✅ Pass / ❌ Fail
Notes: ___________________________________

T104-T105 Results: ✅ Pass / ❌ Fail
Notes: ___________________________________

T109 Results: ✅ Pass / ❌ Fail
Notes: ___________________________________

Overall Status: ✅ Ready for Production / ⚠️ Minor Issues / ❌ Needs Work

Critical Issues Found:
1. ___________________________________
2. ___________________________________
3. ___________________________________

Non-Critical Issues Found:
1. ___________________________________
2. ___________________________________

Recommendations:
___________________________________
___________________________________
```

---

## Next Steps

After completing manual testing:

1. **Document Issues:** File any bugs found in GitHub Issues
2. **Automated Tests:** Consider writing Playwright E2E tests for these scenarios
3. **Performance Testing:** Measure retry timing accuracy
4. **Accessibility Audit:** Run aXe or Lighthouse for WCAG compliance
5. **User Acceptance Testing:** Have real users test the flows

---

**Last Updated:** 2025-12-22
**Status:** Ready for Testing
**Approver:** _______________
**Sign-off Date:** _______________
