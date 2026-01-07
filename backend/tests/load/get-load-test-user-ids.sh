#!/bin/bash
# Script to get load test user IDs from auth-server database

echo "Getting load test user IDs from auth-server database..."
echo ""

# Read DATABASE_URL from auth-server/.env
if [ -f "auth-server/.env" ]; then
    DATABASE_URL=$(grep "^DATABASE_URL=" auth-server/.env | cut -d '=' -f2- | tr -d '"' | tr -d "'")

    if [ -z "$DATABASE_URL" ]; then
        echo "❌ DATABASE_URL not found in auth-server/.env"
        exit 1
    fi

    echo "Querying database for load test users..."
    echo ""

    # Query for load test user IDs
    psql "$DATABASE_URL" -t -c "SELECT id FROM \"user\" WHERE email LIKE 'loadtest_user_%@example.com';" > /tmp/load_test_user_ids.txt

    # Count and display
    COUNT=$(wc -l < /tmp/load_test_user_ids.txt | tr -d ' ')
    echo "Found $COUNT load test users"
    echo ""

    if [ "$COUNT" -gt 0 ]; then
        echo "User IDs (first 10):"
        head -10 /tmp/load_test_user_ids.txt | sed 's/^/  /'

        if [ "$COUNT" -gt 10 ]; then
            echo "  ... and $((COUNT - 10)) more"
        fi

        echo ""
        echo "All IDs saved to: /tmp/load_test_user_ids.txt"
        echo ""
        echo "To clean up these users' data from backend database:"
        echo "  cd backend"

        # Create comma-separated list
        USER_IDS=$(cat /tmp/load_test_user_ids.txt | tr -d ' ' | tr '\n' ',' | sed 's/,$//')

        echo "  uv run python tests/load/cleanup_load_test_data_safe.py --user-ids '$USER_IDS' --dry-run"
        echo ""
        echo "After reviewing, remove --dry-run to actually delete"
    else
        echo "No load test users found"
    fi
else
    echo "❌ auth-server/.env file not found"
    echo ""
    echo "Manual steps:"
    echo "1. Get your DATABASE_URL from auth-server/.env"
    echo "2. Run this query:"
    echo "   SELECT id FROM \"user\" WHERE email LIKE 'loadtest_user_%@example.com';"
    echo ""
    echo "Or use Neon Console:"
    echo "  https://console.neon.tech → SQL Editor"
fi
