<!--
Sync Impact Report:
- Version change: N/A (initial version) → 1.0.0
- Modified principles: N/A (initial constitution)
- Added sections: All core sections (initial creation)
- Removed sections: None
- Templates status:
  ✅ plan-template.md: Constitution Check section compatible
  ✅ spec-template.md: User story and requirements structure align
  ✅ tasks-template.md: Test-first workflow and task organization compatible
- Follow-up TODOs: None
- Rationale: Initial constitution establishing TDD-focused Python CLI development standards
-->

# Command-Line Todo Application Constitution

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory for all code:
- Tests MUST be written before implementation
- Tests MUST fail before code is written to make them pass
- Red-Green-Refactor cycle MUST be strictly followed
- No code may be committed without accompanying tests
- Integration tests required for user-facing workflows

**Rationale**: TDD ensures code correctness, prevents regressions, and serves as living documentation. It forces clear thinking about interfaces before implementation and provides confidence during refactoring.

### II. Clean Code & Simplicity

Code quality and maintainability standards:
- MUST follow PEP 8 style guidelines
- MUST use type hints for all function signatures
- MUST keep functions focused and single-purpose (max 20 lines preferred)
- MUST use descriptive variable and function names
- MUST avoid premature optimization or over-engineering
- YAGNI (You Aren't Gonna Need It) principle applies: only implement requested features

**Rationale**: Clean code reduces cognitive load, eases maintenance, and prevents technical debt. Simplicity enables faster iteration and reduces bugs.

### III. Proper Project Structure

Code organization requirements:
- Source code in `src/` directory
- Tests in `tests/` directory with subdirectories for contract/integration/unit
- Clear separation of concerns: models, services, CLI interface
- Each module MUST have a single, clear responsibility
- Dependencies MUST be explicitly declared in project configuration

**Rationale**: Consistent structure enables team scalability, simplifies navigation, and makes testing straightforward. Clear separation prevents tight coupling.

### IV. In-Memory Data Storage

Data management constraints:
- Tasks MUST be stored in memory (no database or file persistence initially)
- Data structures MUST be simple and appropriate to the task (lists, dicts)
- MUST support basic CRUD operations (Create, Read, Update, Delete)
- Data layer MUST be isolated to enable future persistence additions

**Rationale**: In-memory storage keeps the initial implementation simple while proper isolation allows evolution to persistent storage without major refactoring.

### V. Command-Line Interface Excellence

CLI interaction standards:
- MUST provide clear, user-friendly command interface
- MUST display helpful error messages with actionable guidance
- MUST show task status indicators (complete/incomplete)
- MUST support all five basic operations: Add, Delete, Update, View, Mark Complete
- Input validation MUST provide specific error messages
- Output MUST be human-readable and well-formatted

**Rationale**: The CLI is the user's primary interface. Clear interactions reduce friction, prevent errors, and improve user experience.

### VI. UV Package Manager Integration

Tooling and dependency management:
- MUST use UV for package management and virtual environment
- MUST initialize projects with `uv init --package .` command
- MUST specify Python 3.12+ requirement
- MUST declare all dependencies explicitly
- MUST include development dependencies (pytest, linters)
- Project MUST be runnable via UV commands

**Rationale**: UV provides fast, reliable dependency resolution and environment management. Standardizing on UV ensures consistent development environments. The `--package` flag creates proper package structure with src layout.

## Development Workflow

### Red-Green-Refactor Cycle

For every feature or fix:
1. **Red**: Write a failing test that defines desired behavior
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code quality while keeping tests green
4. Commit only when tests pass

### Code Review Standards

All code changes MUST:
- Include tests that verify the change
- Pass all existing tests
- Follow style guidelines (verified by linters)
- Have clear commit messages describing the change
- Reference the user story or requirement being addressed

### Testing Requirements

Minimum test coverage expectations:
- **Contract Tests**: Core data model operations (Task creation, updates, deletion)
- **Integration Tests**: End-to-end user workflows (add task → view → mark complete)
- **Unit Tests**: Business logic and validation functions
- All tests MUST be runnable via `uv run pytest`
- Tests MUST be deterministic and isolated (no shared state)

## Quality Gates

### Pre-Implementation Checklist

Before writing code, verify:
- [ ] User story or requirement is clear and testable
- [ ] Acceptance criteria are defined
- [ ] Test cases are identified
- [ ] Implementation approach maintains simplicity

### Pre-Commit Checklist

Before committing code, verify:
- [ ] All tests pass (`uv run pytest`)
- [ ] Code follows PEP 8 (`uv run ruff check`)
- [ ] Type hints are present and valid (`uv run mypy`)
- [ ] No TODOs or debug code remains
- [ ] Commit message clearly describes the change

## Governance

### Amendment Process

Constitution changes require:
1. Documented rationale for the change
2. Impact analysis on existing code and workflow
3. Version bump according to semantic versioning:
   - **MAJOR**: Backward incompatible principle changes
   - **MINOR**: New principles or sections added
   - **PATCH**: Clarifications or wording improvements
4. Update to dependent templates (plan, spec, tasks)
5. Migration plan if existing code affected

### Compliance Verification

All pull requests and code reviews MUST verify:
- Tests written before implementation
- Clean code standards followed
- Proper structure maintained
- CLI interface meets excellence standards
- Quality gates passed

### Constitution Supremacy

This constitution supersedes all other development practices. When conflicts arise between this document and other guidance, this constitution takes precedence.

**Complexity Justification**: Any deviation from these principles (e.g., skipping tests, adding unnecessary abstractions, using external storage) MUST be explicitly justified with:
- Specific problem being solved
- Why simpler alternatives are insufficient
- Documented in code review or ADR

**Version**: 1.0.0 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-07
