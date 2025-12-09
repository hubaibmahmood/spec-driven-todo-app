---
allowed-tools: Bash(ruff:*), Bash(black:*), Read
description: Format FastAPI code with ruff and black
---

# FastAPI Code Formatter

## Check Formatting

First, check what needs formatting:

!`ruff check app/ --select I --fix`
!`ruff format app/ --check`

## Your Task

Based on the formatting check:

1. **If formatting is needed:**
   - Show which files need formatting
   - Run the formatters to fix issues
   - Summarize changes made

2. **Apply Formatting:**
   ```bash
   ruff check app/ --fix
   ruff format app/
   ```

3. **Verify:**
   - Confirm all files are properly formatted
   - Note any remaining issues
   - Suggest manual fixes if needed

4. **Report:**
   - List formatted files
   - Summarize formatting changes
   - Confirm code is ready for commit
