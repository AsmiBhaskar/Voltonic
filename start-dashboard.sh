#!/bin/bash

# Voltonic Dashboard Startup Script
# This script starts both the backend API and the React dashboard

echo "🚀 Starting Voltonic Energy Management System..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Start backend API
echo "${BLUE}[1/3] Starting Backend API...${NC}"
cd "$(dirname "$0")"
python3 run.py &
BACKEND_PID=$!
echo "${GREEN}✓ Backend API started (PID: $BACKEND_PID)${NC}"
echo ""

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 3

# Check if backend is running
if curl -s http://127.0.0.1:5000/api/health > /dev/null; then
    echo "${GREEN}✓ Backend API is healthy${NC}"
else
    echo "⚠️  Backend API health check failed, but continuing..."
fi
echo ""

# Start dashboard
echo "${BLUE}[2/3] Starting Dashboard...${NC}"
cd dashboard

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dashboard dependencies..."
    npm install
fi

echo "${BLUE}[3/3] Launching dashboard...${NC}"
npm start &
FRONTEND_PID=$!

echo ""
echo "${GREEN}✓ Dashboard started (PID: $FRONTEND_PID)${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ⚡ VOLTONIC DASHBOARD IS RUNNING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📡 Backend API:  http://127.0.0.1:5000"
echo "  🌐 Dashboard:    http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✓ Services stopped"
    exit 0
}

trap cleanup INT TERM

# Wait for both processes
wait
