#!/bin/bash

# Tactical AEGIS Development Server Start Script

echo "========================================="
echo "Tactical AEGIS - Starting Development Servers"
echo "========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    # kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped"
    exit 0
}

trap cleanup INT TERM

# Start Backend
echo "Starting backend server..."
cd backend || exit 1

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run ./scripts/setup.sh first"
    exit 1
fi

source venv/bin/activate

# Start backend in background
python -m app.main &
BACKEND_PID=$!

echo "Backend server started (PID: $BACKEND_PID)"
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/api/docs"
echo ""

cd ..

# Start Frontend (when ready)
# echo "Starting frontend server..."
# cd frontend || exit 1
# npm run dev &
# FRONTEND_PID=$!
# echo "Frontend server started (PID: $FRONTEND_PID)"
# echo "UI: http://localhost:5173"
# echo ""
# cd ..

echo "========================================="
echo "Development servers running"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for all background processes
wait
