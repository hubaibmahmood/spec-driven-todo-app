# Todo App - Spec-Driven Development Example

A feature-rich, interactive command-line todo application built using **Spec-Driven Development (SDD)** methodology. This project demonstrates how to build software systematically from specification to implementation with full traceability.

## Features

### Current Capabilities

- **Interactive Menu System** - Numbered menu (1-6) for easy navigation
- **Create Tasks** - Add tasks with title and optional description
- **View All Tasks** - Display tasks with ID, status (✓/□), title, and truncated description
- **Mark Complete** - Toggle task completion status (idempotent)
- **Delete Tasks** - Remove single or multiple tasks (comma-separated IDs)
- **Update Tasks** - Modify task descriptions with current value preview
- **Session-Based** - In-memory storage maintains data during app session
- **Input Validation** - Field length limits, whitespace handling, and error messages
- **Error Handling** - Graceful failures without crashes

## Quick Start

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/hubaibmahmood/spec-driven-todo-app.git
cd spec-driven-todo-app

# Install dependencies with uv (automatically creates virtual environment)
uv sync
```

### Run the App

```bash
uv run python -m src.cli.main
```

### Usage

Once running, you'll see an interactive menu:

```
==================================================
TODO APP - Main Menu
==================================================
1. Add Task
2. View Tasks
3. Mark Task Complete
4. Delete Task(s)
5. Update Task Description
6. Quit
==================================================
```

**Example workflow:**
1. Select `1` to add a task
2. Enter title: `Buy groceries`
3. Enter description: `Milk, eggs, bread` (or press Enter to skip)
4. Select `2` to view all tasks
5. Select `3` to mark task complete
6. Enter task ID to mark complete
7. Select `6` to quit

## Project Structure

```
spec-driven-todo-app/
├── src/                          # Source code
│   ├── cli/                      # Command-line interface
│   │   ├── main.py              # Interactive menu entry point
│   │   ├── commands.py          # Command handlers (add, view, delete, etc.)
│   │   ├── validators.py        # Input validation functions
│   │   └── exceptions.py        # Custom exceptions
│   ├── models/                   # Data models
│   │   └── task.py              # Task dataclass
│   ├── services/                 # Business logic
│   │   └── task_service.py      # Task operations
│   └── storage/                  # Data persistence
│       ├── memory_store.py      # In-memory CRUD operations
│       └── exceptions.py        # Storage exceptions
├── tests/                        # Test suite
│   ├── contract/                # Data model validation tests
│   ├── integration/             # End-to-end workflow tests
│   └── unit/                    # Component unit tests
├── specs/                        # Feature specifications
│   ├── 001-add-task/            # Add task feature documentation
│   └── 002-crud-operations/     # CRUD operations documentation
├── history/prompts/             # Prompt History Records (PHRs)
│   ├── constitution/            # Project principles
│   ├── 001-add-task/            # Feature 001 development history
│   └── 002-crud-operations/     # Feature 002 development history
└── .specify/                     # SpecKit Plus framework files
```

## Development Workflow

This project follows **Spec-Driven Development (SDD)** using [SpecKit Plus](https://github.com/cyanheads/speckit-plus):

### Feature Development Lifecycle

1. **Specification** (`/sp.specify`)
   - Write business requirements in plain language
   - Define user stories and acceptance criteria
   - Document edge cases and constraints

2. **Planning** (`/sp.plan`)
   - Create technical architecture
   - Design data models and interfaces
   - Define implementation strategy

3. **Task Generation** (`/sp.tasks`)
   - Break down into atomic, testable tasks
   - Organize by user story and priority
   - Identify parallel execution opportunities

4. **Implementation** (`/sp.implement`)
   - Follow TDD: tests before implementation
   - Complete tasks phase by phase
   - Track progress in tasks.md

5. **Git Workflow** (`/sp.git.commit_pr`)
   - Commit with descriptive messages
   - Create pull requests with context
   - Merge to main after review

### Documentation Generated Per Feature

Each feature in `specs/<feature-name>/` includes:

- `spec.md` - Business requirements and user stories
- `plan.md` - Technical architecture and decisions
- `tasks.md` - Atomic implementation tasks
- `data-model.md` - Entity definitions and relationships
- `contracts/` - API interfaces and test contracts
- `research.md` - Technical investigation findings
- `quickstart.md` - Implementation guide

### Traceability

All development sessions are recorded as **Prompt History Records (PHRs)** in `history/prompts/`:

- Full prompt and response text
- Files modified and tests run
- Stage (spec/plan/tasks/implementation)
- Links to related artifacts

## Testing

### Run All Tests

```bash
uv run pytest
```

### Run Specific Test Suites

```bash
# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# Contract tests only
uv run pytest tests/contract/ -v
```

### Test Coverage

```bash
uv run pytest --cov=src --cov-report=html
```

### Linting and Type Checking

```bash
# Run ruff linter
uv run ruff check src/ tests/

# Run mypy type checker
uv run mypy src/
```

## Tech Stack

- **Language**: Python 3.12+
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Testing**: pytest, pytest-cov
- **Linting**: ruff
- **Type Checking**: mypy
- **Storage**: In-memory (dict-based, no persistence)
- **Data Models**: Python dataclasses
- **Development Framework**: [SpecKit Plus](https://github.com/cyanheads/speckit-plus)

## Architecture Decisions

Key architectural choices documented in feature specs:

- **In-memory storage** - Simple dict-based storage for MVP (no persistence)
- **Interactive menu** - Numbered options instead of CLI arguments for better UX
- **Idempotent operations** - Safe to retry (e.g., marking completed tasks)
- **Batch operations** - Delete supports comma-separated IDs
- **TDD approach** - Tests written before implementation
- **Minimal dependencies** - Standard library only, no external frameworks

## Current Limitations

- **No persistence** - Data lost when app quits (session-based)
- **Single user** - No multi-user support or authentication
- **No task filtering** - Cannot filter by status, date, etc.
- **No priority levels** - All tasks treated equally
- **No due dates** - No deadline tracking
- **No search** - Cannot search tasks by keyword
- **No export** - Cannot export to CSV, JSON, etc.

## Future Enhancements

Potential features for future development:

1. **Persistence Layer**
   - File-based storage (JSON, SQLite)
   - Cloud sync (Firebase, PostgreSQL)

2. **Enhanced Task Management**
   - Priority levels (High/Medium/Low)
   - Due dates and reminders
   - Categories/tags
   - Subtasks

3. **Filtering and Search**
   - Filter by status, priority, date
   - Full-text search
   - Sort by different criteria

4. **Export/Import**
   - Export to CSV, JSON, Markdown
   - Import from other todo apps

5. **User Experience**
   - Color-coded output
   - Progress tracking (% complete)
   - Statistics and analytics

## Contributing

This project follows Spec-Driven Development. To contribute:

1. **Specify the feature** - Write a spec in `specs/<feature-name>/spec.md`
2. **Plan the implementation** - Create architecture plan
3. **Generate tasks** - Break down into atomic tasks
4. **Implement with TDD** - Tests first, then code
5. **Document decisions** - Update specs and create PHRs
6. **Submit PR** - Include spec, tests, and implementation

## License

This project is a demonstration of Spec-Driven Development methodology.

## Acknowledgments

- Built with [SpecKit Plus](https://github.com/cyanheads/speckit-plus) - Spec-Driven Development framework
- Developed with [Claude Code](https://claude.com/claude-code) - AI-powered development assistant

## Project Status

**Current Version**: 0.2.0 (CRUD Operations Complete)

### Completed Features

- ✅ 001-add-task - Add tasks with validation
- ✅ 002-crud-operations - Full CRUD with interactive menu

### In Progress

- None

### Planned

- File-based persistence
- Task priorities and due dates
- Filtering and search capabilities

---

**Note**: This is a learning project demonstrating Spec-Driven Development. The focus is on the development process and documentation rather than production-ready features.
