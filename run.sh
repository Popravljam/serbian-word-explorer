#!/bin/bash

# Script to run the Serbian Word Explorer application

echo "🚀 Starting Serbian Word Explorer..."
echo ""

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✓ Backend is already running on port 8000"
else
    echo "Starting backend server..."
    cd backend
    source venv/bin/activate
    nohup python main.py > server.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    echo "✓ Backend started (PID: $BACKEND_PID)"
    sleep 2
fi

# Start frontend server
echo "Starting frontend server..."
cd frontend
echo "✓ Frontend server starting on http://localhost:3000"
echo ""
echo "================================================"
echo "Serbian Word Explorer is ready!"
echo "================================================"
echo ""
echo "Open your browser and navigate to:"
echo "  http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the frontend server"
echo "(Backend will continue running in background)"
echo ""

python3 -m http.server 3000
