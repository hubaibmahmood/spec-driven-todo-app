# Load Testing Scripts

This directory contains scripts for JWT authentication load testing and cleanup.

## Load Testing

### 1. Run Load Test

```bash
# From project root
cd backend

# Start servers first (in separate terminals):
# Terminal 1: cd auth-server && npm run dev
# Terminal 2: cd backend && uv run uvicorn src.api.main:app --reload

# Run load test with web UI
uv run locust -f tests/load/jwt_auth_load_test.py --host http://localhost:8000
# Open http://localhost:8089 in browser

# Or run headless with 100 users
uv run locust -f tests/load/jwt_auth_load_test.py \
    --host http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 2m \
    --headless
```

## Cleanup Scripts

### 2. Clean Up Backend Database (Tasks & Sessions)

```bash
# From project root
cd backend

# Check what's in the database
uv run python tests/load/cleanup_load_test_data_safe.py --stats

# Get load test user IDs (run SQL on Neon database):
# SELECT id FROM "user" WHERE email LIKE 'loadtest_user_%@example.com';

# Clean up for specific user IDs (dry run first)
uv run python tests/load/cleanup_load_test_data_safe.py \
    --user-ids "user1,user2,user3" \
    --dry-run

# Actually delete
uv run python tests/load/cleanup_load_test_data_safe.py \
    --user-ids "user1,user2,user3"
```

### 3. Clean Up Auth-Server Database (Users)

```bash
# From project root
cd auth-server

# Dry run (see what would be deleted)
npm run cleanup:users -- --dry-run

# Actually delete load test users
npm run cleanup:users
```

## Helper Scripts

### Get Load Test User IDs

```bash
# From project root
./backend/tests/load/get-load-test-user-ids.sh
```

This script:
- Reads DATABASE_URL from `auth-server/.env`
- Queries for all load test user IDs
- Provides the exact cleanup command

### Start Services (Optional Helper)

```bash
# Note: This script needs to be run from project root
cd ../../..  # Go to project root
./backend/tests/load/start-load-test.sh
```

Or start services manually (recommended):
```bash
# Terminal 1
cd auth-server
npm run dev

# Terminal 2
cd backend
uv run uvicorn src.api.main:app --reload
```

## Files

- `jwt_auth_load_test.py` - Main load test script using Locust
- `cleanup_load_test_data_safe.py` - Safe cleanup for backend database
- `get-load-test-user-ids.sh` - Helper to get user IDs from auth-server DB
- `start-load-test.sh` - Helper to start both services
- `__init__.py` - Python package marker

## Performance Metrics

After running tests, check Prometheus metrics:

```bash
curl http://localhost:8000/metrics | grep auth_validation
```

Expected results:
- JWT validation: **< 1ms p95** ✅
- Auth queries/sec: **< 5/sec** (vs 167/sec baseline) ✅
- Zero failure rate with proper authentication ✅
