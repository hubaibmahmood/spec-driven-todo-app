#!/bin/bash
# Script to start auth-server and backend for load testing

echo "🚀 Starting services for JWT load testing..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if auth-server is already running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}✓${NC} Auth-server already running on port 8080"
else
    echo -e "${YELLOW}→${NC} Starting auth-server on port 8080..."
    cd auth-server
    npm run dev > ../auth-server.log 2>&1 &
    AUTH_PID=$!
    cd ..
    echo -e "${GREEN}✓${NC} Auth-server started (PID: $AUTH_PID)"
    echo "  Log: tail -f auth-server.log"
fi

# Wait for auth-server to be ready
echo -e "${YELLOW}→${NC} Waiting for auth-server to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Auth-server is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗${NC} Auth-server failed to start. Check auth-server.log"
        exit 1
    fi
done

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}✓${NC} Backend already running on port 8000"
else
    echo -e "${YELLOW}→${NC} Starting backend on port 8000..."
    cd backend
    uv run uvicorn src.api.main:app --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"
    echo "  Log: tail -f backend.log"
fi

# Wait for backend to be ready
echo -e "${YELLOW}→${NC} Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗${NC} Backend failed to start. Check backend.log"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}🎉 All services ready for load testing!${NC}"
echo ""
echo "Services running:"
echo "  • Auth-server: http://localhost:8080"
echo "  • Backend API: http://localhost:8000"
echo "  • Prometheus metrics: http://localhost:8000/metrics"
echo ""
echo "Run load test:"
echo "  cd backend"
echo "  uv run locust -f tests/load/jwt_auth_load_test.py --host http://localhost:8000"
echo "  # Then open http://localhost:8089 in your browser"
echo ""
echo "Or run headless:"
echo "  cd backend"
echo "  uv run locust -f tests/load/jwt_auth_load_test.py \\"
echo "      --host http://localhost:8000 \\"
echo "      --users 100 \\"
echo "      --spawn-rate 10 \\"
echo "      --run-time 2m \\"
echo "      --headless"
echo ""
echo "View logs:"
echo "  tail -f auth-server.log"
echo "  tail -f backend.log"
echo ""
echo "Stop services:"
echo "  kill \$(lsof -t -i:8080)  # Stop auth-server"
echo "  kill \$(lsof -t -i:8000)  # Stop backend"
