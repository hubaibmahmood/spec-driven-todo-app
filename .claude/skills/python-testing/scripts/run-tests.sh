#!/bin/bash

# FastAPI Test Runner Script
# This script provides convenient commands for running tests with various options

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
COVERAGE_THRESHOLD=80
VERBOSE=false
FAST_FAIL=false
PARALLEL=false
MARKERS=""
TEST_PATH="tests/"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

FastAPI Test Runner - Run tests with various configurations

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Verbose output
    -f, --fast-fail         Stop at first failure
    -p, --parallel          Run tests in parallel
    -c, --coverage          Run with coverage report
    -m, --markers MARKERS   Run only tests matching markers (e.g., "not slow")
    -t, --threshold NUM     Coverage threshold percentage (default: 80)
    --unit                  Run only unit tests
    --integration           Run only integration tests
    --smoke                 Run only smoke tests
    --watch                 Watch mode (re-run on file changes)
    PATH                    Specific test file or directory (default: tests/)

EXAMPLES:
    $0                                      # Run all tests
    $0 -v -c                                # Run with verbose output and coverage
    $0 -f -m "not slow"                     # Stop at first failure, skip slow tests
    $0 --unit                               # Run only unit tests
    $0 -p -c tests/test_users.py            # Run specific file with coverage in parallel
    $0 --watch                              # Watch mode

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--fast-fail)
            FAST_FAIL=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -m|--markers)
            MARKERS="$2"
            shift 2
            ;;
        -t|--threshold)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        --unit)
            MARKERS="unit"
            shift
            ;;
        --integration)
            MARKERS="integration"
            shift
            ;;
        --smoke)
            MARKERS="smoke"
            shift
            ;;
        --watch)
            WATCH=true
            shift
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Install it with: pip install pytest pytest-asyncio pytest-cov"
    exit 1
fi

# Build pytest command
PYTEST_CMD="pytest"

# Add test path
PYTEST_CMD="$PYTEST_CMD $TEST_PATH"

# Add verbose flag
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -vv"
fi

# Add fast fail flag
if [ "$FAST_FAIL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -x"
fi

# Add markers
if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m \"$MARKERS\""
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=$COVERAGE_THRESHOLD"
fi

# Add parallel execution
if [ "$PARALLEL" = true ]; then
    # Check if pytest-xdist is installed
    if python -c "import xdist" 2>/dev/null; then
        PYTEST_CMD="$PYTEST_CMD -n auto"
    else
        print_warning "pytest-xdist not installed. Running tests sequentially."
        print_info "Install with: pip install pytest-xdist"
    fi
fi

# Watch mode
if [ "$WATCH" = true ]; then
    # Check if pytest-watch is installed
    if command -v ptw &> /dev/null; then
        print_info "Running tests in watch mode..."
        ptw -- $PYTEST_CMD
        exit 0
    else
        print_warning "pytest-watch not installed. Install with: pip install pytest-watch"
        print_info "Falling back to regular test run..."
    fi
fi

# Print command
print_info "Running command: $PYTEST_CMD"
echo ""

# Run tests
eval $PYTEST_CMD
EXIT_CODE=$?

echo ""

# Print results
if [ $EXIT_CODE -eq 0 ]; then
    print_success "All tests passed! ✅"

    if [ "$COVERAGE" = true ]; then
        print_success "Coverage report generated in htmlcov/index.html"
        print_info "Open with: open htmlcov/index.html"
    fi
else
    print_error "Tests failed! ❌"
    exit $EXIT_CODE
fi

exit 0
