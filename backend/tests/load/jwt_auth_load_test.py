"""
Load testing script for JWT authentication performance.

This script simulates 1000+ concurrent users making authenticated API requests
to measure JWT auth performance vs session-based auth baseline.

Target metrics:
- Auth validation latency: <1ms p95 for JWT (vs ~10-20ms for session)
- Database auth query rate: <5 queries/sec for JWT (vs ~167 queries/sec baseline)

Prerequisites:
    1. Auth-server must be running on port 8080:
       cd auth-server && npm run dev

    2. Backend must be running on port 8000:
       cd backend && uv run uvicorn src.api.main:app --reload

Usage:
    # Run load test with 100 users (recommended for testing)
    cd backend
    uv run locust -f tests/load/jwt_auth_load_test.py --host http://localhost:8000 --users 100 --spawn-rate 10 --run-time 2m --headless

    # Run with web UI (access at http://localhost:8089)
    uv run locust -f tests/load/jwt_auth_load_test.py --host http://localhost:8000

    # Full scale test with 1000 users
    uv run locust -f tests/load/jwt_auth_load_test.py --host http://localhost:8000 --users 1000 --spawn-rate 50 --run-time 5m --headless --csv results
"""

import random
import time
from locust import HttpUser, task, between, events
from datetime import datetime

# Track metrics globally
auth_query_count = 0
auth_query_start_time = None


class TodoAppUser(HttpUser):
    """Simulates a user interacting with the Todo App with JWT authentication."""

    # Wait 1-3 seconds between requests (simulates real user behavior)
    wait_time = between(1, 3)

    def on_start(self):
        """
        Called when a simulated user starts.
        Registers and logs in to get JWT access token.
        """
        # Register a unique test user
        user_num = random.randint(1, 1000000)
        self.email = f"loadtest_user_{user_num}@example.com"
        self.password = "LoadTest123!"
        self.access_token = None
        self.user_id = None
        self.created_task_ids = []  # Track created tasks for cleanup

        # Register and login to get real JWT token
        self.login()

    def on_stop(self):
        """
        Called when a simulated user stops.
        Cleanup: Delete all tasks created by this user.
        """
        if not self.access_token:
            return

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # Delete all tasks created by this user
        try:
            # Get all tasks for this user
            response = self.client.get("/tasks/", headers=headers, catch_response=True)
            if response.status_code == 200:
                tasks = response.json()
                task_ids = [task['id'] for task in tasks]

                # Bulk delete if there are tasks
                if task_ids:
                    self.client.post(
                        "/tasks/bulk-delete",
                        json={"task_ids": task_ids},
                        headers=headers,
                        catch_response=True
                    )
        except Exception as e:
            # Cleanup errors are non-critical
            pass

    def login(self):
        """Login and obtain JWT access token from auth-server."""
        # Register user via auth-server (http://localhost:8080)
        # Uses JWT-specific endpoints that return access tokens

        # Try to register (will fail if user exists, which is ok)
        try:
            register_response = self.client.post(
                "http://localhost:8080/api/auth/jwt/sign-up",
                json={
                    "email": self.email,
                    "password": self.password,
                    "name": f"Load Test User"
                },
                catch_response=True
            )

            if register_response.status_code == 200:
                # Registration successful, extract token
                data = register_response.json()
                self.access_token = data.get("accessToken")
                self.user_id = data.get("user", {}).get("id")
                if self.access_token:
                    return  # Success, we're done
        except Exception as e:
            # User might already exist, try login
            pass

        # Login to get JWT token (if registration failed or user exists)
        try:
            login_response = self.client.post(
                "http://localhost:8080/api/auth/jwt/sign-in",
                json={
                    "email": self.email,
                    "password": self.password
                }
            )

            if login_response.status_code == 200:
                data = login_response.json()
                self.access_token = data.get("accessToken")
                self.user_id = data.get("user", {}).get("id")
            else:
                # Login failed
                print(f"Login failed with status {login_response.status_code}: {login_response.text[:100]}")
                self.access_token = None
                self.user_id = None
        except Exception as e:
            # If auth-server is not available, skip authentication
            print(f"Warning: Could not authenticate: {e}")
            self.access_token = None
            self.user_id = None

    @task(5)
    def get_tasks(self):
        """
        Fetch user's tasks (most common operation).
        Weight: 5 (5x more likely than other tasks)

        This endpoint requires JWT authentication, so it will:
        1. Extract Bearer token from Authorization header
        2. Validate JWT signature (stateless, no DB query)
        3. Extract user_id from token
        4. Query tasks for user
        """
        # Skip if no valid access token
        if not self.access_token:
            # Try to re-login
            self.login()
            if not self.access_token:
                return  # Still no token, skip this request

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        with self.client.get(
            "/tasks/",
            headers=headers,
            catch_response=True,
            name="/tasks/ (authenticated)"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Token might be expired, try to refresh
                self.refresh_token()
                response.failure("Token expired, refreshing")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(3)
    def create_task(self):
        """
        Create a new task.
        Weight: 3 (3x baseline frequency)

        Requires JWT authentication.
        """
        if not self.access_token:
            return

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        task_data = {
            "title": f"Load Test Task {random.randint(1, 10000)}",
            "description": "Generated by load testing",
            "priority": random.choice(["Low", "Medium", "High", "Urgent"])
            # Note: No "completed" field - that's only for updates, not creation
        }

        with self.client.post(
            "/tasks/",
            json=task_data,
            headers=headers,
            catch_response=True,
            name="/tasks/ (create)"
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 401:
                self.refresh_token()
                response.failure("Token expired, refreshing")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(2)
    def update_task(self):
        """
        Update an existing task.
        Weight: 2 (2x baseline frequency)

        Requires JWT authentication.
        """
        if not self.access_token:
            return

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # Mock task ID (in real scenario, would fetch actual task IDs)
        task_id = random.randint(1, 100)

        update_data = {
            "completed": random.choice([True, False]),
            "priority": random.choice(["Low", "Medium", "High", "Urgent"])
        }

        with self.client.patch(
            f"/tasks/{task_id}",
            json=update_data,
            headers=headers,
            catch_response=True,
            name="/tasks/:id (update)"
        ) as response:
            if response.status_code in [200, 404]:  # 404 is ok for mock IDs
                response.success()
            elif response.status_code == 401:
                self.refresh_token()
                response.failure("Token expired, refreshing")
            else:
                response.failure(f"Got status {response.status_code}")

    # Removed @task decorator - this is called when tokens expire, not as a scheduled task
    # The refresh endpoint requires httpOnly cookies which Locust can't easily simulate
    def refresh_token(self):
        """
        Called when JWT access token expires (from 401 responses).

        Note: This will always fail because the backend refresh endpoint requires
        a refresh token cookie, which Locust doesn't have. When this is called,
        we just re-login instead.
        """
        # Instead of calling the refresh endpoint (which needs cookies),
        # just re-login to get a new token
        self.login()


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    global auth_query_start_time
    auth_query_start_time = time.time()
    print("\n" + "="*60)
    print("JWT Authentication Load Test Starting")
    print("="*60)
    print(f"Target: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("\nExpected Results:")
    print("  - JWT validation latency: <1ms p95")
    print("  - Auth queries/sec: <5 (vs 167 baseline)")
    print("  - No database queries for JWT signature validation")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops. Print summary statistics."""
    global auth_query_start_time

    elapsed_time = time.time() - auth_query_start_time if auth_query_start_time else 1

    print("\n" + "="*60)
    print("JWT Authentication Load Test Complete")
    print("="*60)

    # Get stats from environment
    stats = environment.stats

    print("\nRequest Statistics:")
    print(f"  Total Requests: {stats.total.num_requests}")
    print(f"  Failures: {stats.total.num_failures}")
    print(f"  Median Response Time: {stats.total.median_response_time}ms")
    print(f"  95th Percentile: {stats.total.get_response_time_percentile(0.95)}ms")
    print(f"  99th Percentile: {stats.total.get_response_time_percentile(0.99)}ms")
    print(f"  Requests/sec: {stats.total.total_rps:.2f}")

    # Auth-specific metrics (would need Prometheus metrics to get actual values)
    print("\nAuthentication Metrics:")
    print("  To view actual JWT validation times and auth query rates:")
    print("  1. Access Prometheus metrics at http://localhost:8000/metrics")
    print("  2. Look for 'auth_validation_seconds' histogram")
    print("  3. Look for 'token_refresh_total' and 'token_refresh_errors_total' counters")

    print("\nSuccess Criteria:")
    jwt_validation_time = stats.total.get_response_time_percentile(0.95)
    if jwt_validation_time < 100:  # <100ms for entire request is good
        print("  ✓ Response time within acceptable range")
    else:
        print(f"  ✗ Response time high: {jwt_validation_time}ms (investigate)")

    failure_rate = (stats.total.num_failures / stats.total.num_requests * 100) if stats.total.num_requests > 0 else 0
    if failure_rate < 1:
        print(f"  ✓ Failure rate low: {failure_rate:.2f}%")
    else:
        print(f"  ✗ Failure rate high: {failure_rate:.2f}% (investigate)")

    print("\nNext Steps:")
    print("  1. Check Prometheus metrics for auth_validation_seconds{method='jwt'}")
    print("  2. Monitor database query logs for auth-related queries")
    print("  3. Compare JWT vs session auth performance")
    print("="*60 + "\n")


if __name__ == "__main__":
    import os
    import sys

    # Add helpful usage message
    print("""
JWT Authentication Load Testing Script
======================================

This script uses Locust to simulate 1000+ concurrent users and measure:
- JWT validation latency (target: <1ms p95)
- Database auth query rate (target: <5 queries/sec)

Usage:
------
1. Start the auth-server (REQUIRED):
   cd auth-server && npm run dev
   # Auth-server will run on port 8080

2. Start the backend server:
   cd backend && uv run uvicorn src.api.main:app --reload
   # Backend will run on port 8000

3. Run load test (choose one):

   # Web UI (recommended for first time):
   cd backend
   uv run locust -f tests/load/jwt_auth_load_test.py --host http://localhost:8000
   # Then open http://localhost:8089 in browser

   # Quick test with 100 users:
   cd backend
   uv run locust -f tests/load/jwt_auth_load_test.py \\
       --host http://localhost:8000 \\
       --users 100 \\
       --spawn-rate 10 \\
       --run-time 2m \\
       --headless

   # Full scale test with 1000 users:
   cd backend
   uv run locust -f tests/load/jwt_auth_load_test.py \\
       --host http://localhost:8000 \\
       --users 1000 \\
       --spawn-rate 50 \\
       --run-time 5m \\
       --headless \\
       --csv results

4. View Prometheus metrics:
   curl http://localhost:8000/metrics | grep auth_validation

Notes:
------
- This script registers and logs in real users via auth-server (port 8080)
- Each virtual user gets a unique email and JWT access token
- Tests full authentication flow: register → login → get JWT → make requests
- Monitor database query logs during test to verify <5 auth queries/sec
- Compare results with session-based auth baseline (167 queries/sec)
""")
