# Feature Specification: Interactive Todo Menu with CRUD Operations

**Feature Branch**: `002-crud-operations`
**Created**: 2025-12-07
**Status**: Draft
**Input**: User description: "lets add view tasks, delete tasks, update tasks and mark task completed features to our todo app. View tasks should display list of tasks with id and their status. detele tasks will take id or ids seperated by commas and delete all the tasks with the given ids, update task will take id and the description to update that tasks description. Mark task complete will take id and mark it complete. Add feature we have already implemented in our 001 specs. This app is command line based but not aruguments style. It will be an interactive style. User runs the program. Then It should show the option to add, update, delete, view task lists, mark complete and quit options. Then we select the option perfrom task then it again shows these options so it has all the tasks in its memory untill we select quit and the program exists lossing all the tasks that's what cli progam was supposed to do."

## Clarifications

### Session 2025-12-07

- Q: Should the Update Task feature allow updating the task title, or only the description? → A: Users can update only description (title is immutable)
- Q: How should users select menu options - numbered choices (1-6) or text commands (add/view/delete/etc.)? → A: Numbered choices (user enters 1-6)
- Q: What should happen when a user tries to mark an already-completed task as complete again? → A: Idempotent: show informational message "Task is already complete"
- Q: When viewing the task list, should the description be displayed for each task, or only ID, title, and status? → A: Show ID, title, status, and first 50 characters of description
- Q: Should there be a way to view the full description of a task (beyond the 50-character truncation)? → A: No separate detail view; full description visible only during update

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View All Tasks (Priority: P1)

As a user, I want to view all my tasks with their IDs and status so I can see what I need to do.

**Why this priority**: Viewing tasks is fundamental - users need to see what tasks exist before they can interact with them. Without this, the application provides no visibility into the todo list.

**Independent Test**: Can be fully tested by adding several tasks (with different statuses), then selecting the view option and confirming all tasks appear with correct IDs, titles, and status indicators.

**Acceptance Scenarios**:

1. **Given** I have added 3 tasks, **When** I select the "View Tasks" option, **Then** I see all 3 tasks listed with their IDs, titles, status (complete/incomplete), and first 50 characters of description
2. **Given** no tasks exist, **When** I select the "View Tasks" option, **Then** I see a message indicating "No tasks found" or similar
3. **Given** I have tasks with different statuses, **When** I view the task list, **Then** I can clearly distinguish between completed and incomplete tasks
4. **Given** I have a task with description longer than 50 characters, **When** I view the task list, **Then** I see the first 50 characters followed by "..." truncation indicator

---

### User Story 2 - Mark Task as Complete (Priority: P1)

As a user, I want to mark a task as complete so I can track my progress.

**Why this priority**: Marking tasks complete is core functionality - it provides the sense of accomplishment and progress tracking that makes todo apps valuable. This is essential for the minimum viable product.

**Independent Test**: Can be tested independently by adding a task, marking it complete by ID, then viewing the task list to confirm the status changed from incomplete to complete.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task with ID 5, **When** I select "Mark Complete" and enter ID 5, **Then** the task is marked as complete and confirmation is shown
2. **Given** I have marked a task as complete, **When** I view the task list, **Then** the task displays with a completed status indicator
3. **Given** I attempt to mark a non-existent task ID as complete, **When** I submit the ID, **Then** I see an error message indicating the task was not found

---

### User Story 3 - Delete Single or Multiple Tasks (Priority: P2)

As a user, I want to delete one or more tasks by ID so I can remove items I no longer need.

**Why this priority**: Deletion is important for task management but not required for the absolute minimum product. Users can work around this by ignoring unwanted tasks, though it's not ideal.

**Independent Test**: Can be tested by adding multiple tasks, deleting specific tasks by ID (both single and comma-separated), then viewing the list to confirm only the specified tasks were removed.

**Acceptance Scenarios**:

1. **Given** I have tasks with IDs 1, 2, 3, **When** I select "Delete Tasks" and enter ID "2", **Then** only task 2 is deleted and I see confirmation
2. **Given** I have tasks with IDs 1, 2, 3, 4, 5, **When** I enter "1,3,5" (comma-separated), **Then** tasks 1, 3, and 5 are deleted and I see confirmation listing all deleted task IDs
3. **Given** I attempt to delete a non-existent task ID, **When** I submit the ID, **Then** I see an error message for that specific ID but valid IDs are still deleted
4. **Given** I enter invalid input (non-numeric), **When** I submit, **Then** I see an error message explaining the expected format

---

### User Story 4 - Update Task Description (Priority: P3)

As a user, I want to update a task's description so I can modify or add details without recreating the task.

**Why this priority**: While useful, updating descriptions is a convenience feature. Users can work around this by deleting and recreating tasks, though it's less efficient.

**Independent Test**: Can be tested by adding a task with a description, updating it by ID with new description text, then viewing the task details to confirm the description changed while title and ID remained the same.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 3, **When** I select "Update Task" and provide ID 3, **Then** the full task description is displayed for editing
2. **Given** I update a task's description with new text "Updated details here", **When** I submit the update, **Then** the task's description is updated and confirmation is shown
3. **Given** I update a task's description, **When** I view the task list, **Then** I see the new description (first 50 chars) while the title and ID remain unchanged
4. **Given** I attempt to update a non-existent task ID, **When** I submit the ID, **Then** I see an error message indicating the task was not found
5. **Given** I provide an empty description, **When** I update the task, **Then** the description is cleared (set to empty)

---

### User Story 5 - Interactive Menu Loop (Priority: P1)

As a user, I want to see a menu of options after each action so I can perform multiple operations in one session without restarting the program.

**Why this priority**: The interactive loop is the core interface paradigm for this application. Without it, users would need to restart the program for each operation, making the tool impractical.

**Independent Test**: Can be tested by launching the program, performing any action (e.g., add task), then confirming the menu reappears, performing another action, confirming the menu reappears again, and finally selecting quit to exit.

**Acceptance Scenarios**:

1. **Given** I launch the application, **When** the program starts, **Then** I see a menu with options: Add Task, View Tasks, Update Task, Delete Tasks, Mark Complete, Quit
2. **Given** I complete any action (add, view, update, delete, mark complete), **When** the action finishes, **Then** I see the same menu again without needing to restart
3. **Given** I am viewing the menu, **When** I select "Quit", **Then** the program exits gracefully
4. **Given** I enter an invalid menu option, **When** I submit, **Then** I see an error message and the menu is displayed again

---

### Edge Cases

- **Empty task list operations**: When no tasks exist, view shows empty message; delete, update, and mark complete show appropriate error messages
- **Invalid task IDs**: Non-existent IDs show error messages without crashing; partial success for comma-separated deletes (valid IDs processed, invalid IDs reported)
- **Invalid input formats**: Non-numeric IDs, malformed comma-separated lists handled gracefully with error messages
- **Multiple IDs with whitespace**: "1, 2, 3" (with spaces) should work the same as "1,2,3"
- **Duplicate IDs in delete list**: "1,1,2" should delete tasks 1 and 2 only once and not error
- **Description character limits on update**: Same 1000-character limit as add task (with warning and truncation behavior)
- **Description truncation in list view**: Descriptions longer than 50 characters display first 50 chars + "..."; tasks with no description show empty description field
- **Completing already completed task**: Operation is idempotent; displays informational message "Task is already complete" without treating it as an error
- **Invalid menu selections**: Out-of-range numbers (0, 7, 99) or non-numeric input handled with error message and menu re-display

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display an interactive menu with numbered options (1-6): 1. Add Task, 2. View Tasks, 3. Update Task, 4. Delete Tasks, 5. Mark Complete, 6. Quit
- **FR-002**: System MUST return to the main menu after completing any operation (add, view, update, delete, mark complete)
- **FR-003**: System MUST allow users to view all tasks showing ID, title, status (complete/incomplete), and first 50 characters of description (truncated with "..." if longer) for each task
- **FR-004**: System MUST display a clear message when the task list is empty (e.g., "No tasks found")
- **FR-005**: System MUST allow users to mark a task as complete by providing the task ID
- **FR-006**: System MUST update the task status from incomplete to complete when mark complete is successful
- **FR-006a**: System MUST handle marking an already-completed task as idempotent operation, displaying informational message "Task is already complete" without error
- **FR-007**: System MUST allow users to delete one or more tasks by providing a single ID or comma-separated IDs
- **FR-008**: System MUST handle comma-separated task IDs for deletion, processing each ID and deleting all valid tasks
- **FR-009**: System MUST handle whitespace in comma-separated ID lists (e.g., "1, 2, 3" works same as "1,2,3")
- **FR-010**: System MUST allow users to update a task's description by providing the task ID and new description text; task title cannot be updated and remains immutable
- **FR-010a**: System MUST display the full current description when user initiates update operation on a task
- **FR-011**: System MUST preserve the task title and ID when updating description; title is immutable after task creation
- **FR-012**: System MUST validate task IDs for all operations (mark complete, delete, update) and show error messages for non-existent IDs
- **FR-013**: System MUST provide clear confirmation messages after successful operations showing what was changed
- **FR-014**: System MUST provide clear error messages for invalid operations (non-existent IDs, invalid input formats)
- **FR-015**: System MUST exit gracefully when user selects the "Quit" option, losing all tasks from memory
- **FR-016**: System MUST handle invalid menu selections (non-numeric or out of range 1-6) and re-display the menu with an error message
- **FR-017**: System MUST accept single-digit numeric input (1-6) for menu selection
- **FR-018**: System MUST integrate with existing add task functionality from feature 001-add-task
- **FR-019**: System MUST apply the same description character limit (1000 characters) when updating tasks, with warning and truncation behavior
- **FR-020**: System MUST handle duplicate IDs in delete lists without errors (delete each task only once)

### Key Entities

- **Task**: Represents a single todo item (from 001-add-task spec) with attributes:
  - Unique identifier (integer, sequential)
  - Title (required, 1-200 characters)
  - Description (optional, 0-1000 characters)
  - Status (boolean: incomplete or complete)
  - Created timestamp

- **Menu**: Represents the interactive interface with options:
  - Add Task (invokes 001-add-task functionality)
  - View Tasks (displays all tasks with ID, title, status, and first 50 chars of description)
  - Update Task (modifies task description by ID)
  - Delete Tasks (removes tasks by single or comma-separated IDs)
  - Mark Complete (changes task status by ID)
  - Quit (exits application, loses all data)

### Assumptions

- Tasks are displayed in order of creation (by ID) in the view list
- Status indicators use clear text labels like "[✓] Complete" and "[ ] Incomplete" or similar visual markers
- Task list view shows first 50 characters of description; descriptions longer than 50 characters are truncated with "..." appended
- Tasks with no description show empty description field in list view
- No separate "View Task Details" menu option; full description is only visible when user selects "Update Task"
- Update task operation displays full current description before allowing edits
- Comma-separated delete accepts any whitespace around commas
- Updating a task with empty description clears the description field
- Marking an already-completed task as complete is idempotent; displays "Task is already complete" informational message
- Menu uses numbered options (1-6) for user selection; users enter a single digit to choose an action
- All tasks remain in memory throughout the session until quit is selected

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view the complete task list in under 2 seconds from menu selection
- **SC-002**: Users can mark a task complete by ID in under 5 seconds (including menu navigation)
- **SC-003**: Users can delete multiple tasks (up to 10) in a single operation in under 5 seconds
- **SC-004**: Users can update a task description in under 10 seconds (including menu navigation and text entry)
- **SC-005**: 100% of operations return to the main menu without requiring program restart
- **SC-006**: 100% of invalid inputs (non-existent IDs, malformed input) show clear error messages without crashing
- **SC-007**: Users can perform at least 20 consecutive operations in a single session without errors
- **SC-008**: Task status changes (mark complete) are immediately visible in the next view operation
- **SC-009**: Deleted tasks are immediately removed from the task list with no orphaned data
- **SC-010**: Program exits cleanly in under 1 second when quit is selected
