---
allowed-tools: Bash(pytest:*), Bash(python:*), Read
description: Run FastAPI project tests with pytest and coverage reporting
---

# FastAPI Test Runner

## Run Tests

Run the test suite with coverage:

!`pytest --cov=app --cov-report=term-missing --cov-report=html -vv`

## Your Task

Based on the test results above:

1. **Analyze Results:**
   - Identify any failing tests
   - Review coverage percentage
   - Note missing test coverage areas

2. **If Tests Pass:**
   - Summarize test results (total tests, passed, coverage %)
   - Identify areas with low coverage (< 80%)
   - Suggest additional tests if needed

3. **If Tests Fail:**
   - Identify which tests failed
   - Show the failure reasons
   - Suggest fixes for failing tests
   - Offer to implement fixes if requested

4. **Coverage Report:**
   - Show coverage summary
   - Highlight files with low coverage
   - Note: Full HTML report available in `htmlcov/index.html`
