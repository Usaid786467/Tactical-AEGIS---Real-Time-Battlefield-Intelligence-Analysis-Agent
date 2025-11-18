#!/bin/bash

# Tactical AEGIS Test Runner Script

echo "========================================="
echo "Tactical AEGIS - Running All Tests"
echo "========================================="
echo ""

# Test Backend
echo "Testing backend..."
cd backend || exit 1

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run ./scripts/setup.sh first"
    exit 1
fi

source venv/bin/activate

echo "Running backend tests..."
pytest tests/ -v --cov=app --cov-report=term-missing

BACKEND_EXIT_CODE=$?

echo ""
if [ $BACKEND_EXIT_CODE -eq 0 ]; then
    echo "✅ Backend tests passed"
else
    echo "❌ Backend tests failed"
fi

cd ..

# Test Frontend (when ready)
# echo ""
# echo "Testing frontend..."
# cd frontend || exit 1
# npm test
# FRONTEND_EXIT_CODE=$?
# echo ""
# if [ $FRONTEND_EXIT_CODE -eq 0 ]; then
#     echo "✅ Frontend tests passed"
# else
#     echo "❌ Frontend tests failed"
# fi
# cd ..

echo ""
echo "========================================="
if [ $BACKEND_EXIT_CODE -eq 0 ]; then
    echo "All tests passed! ✅"
    exit 0
else
    echo "Some tests failed ❌"
    exit 1
fi
