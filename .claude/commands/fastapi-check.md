---
allowed-tools: Bash(mypy:*), Bash(ruff:*), Read
description: Run type checking and linting on FastAPI code
---

# FastAPI Code Quality Check

## Run Checks

Run type checking and linting:

!`mypy app/ --ignore-missing-imports --check-untyped-defs || echo "Mypy check completed with errors"`
!`ruff check app/ || echo "Ruff check completed with errors"`

## Your Task

Based on the check results:

1. **Analyze Issues:**
   - Review type errors from mypy
   - Review linting errors from ruff
   - Categorize issues by severity

2. **Report Findings:**
   - **Type Errors:** List files with type issues
   - **Lint Errors:** List files with lint issues
   - **Warnings:** Note any warnings

3. **Suggest Fixes:**
   - For each issue, suggest how to fix it
   - Prioritize critical issues
   - Offer to implement fixes if requested

4. **Summary:**
   - Total errors and warnings
   - Files needing attention
   - Pass/fail status

If all checks pass:
- Confirm code quality is good
- Note any minor improvements possible
- Code is ready for commit
