#!/bin/bash

# Voltonic Full Restart Script
# This script completely restarts the backend with fresh data

echo "🔄 Restarting Voltonic Energy Management System..."
echo ""

# Step 1: Kill existing Flask process
echo "1️⃣  Killing existing Flask server on port 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null
echo "   ✓ Port 5000 freed"
echo ""

# Step 2: Delete old database
echo "2️⃣  Removing old database..."
rm -f instance/voltonic.db
echo "   ✓ Database deleted"
echo ""

# Step 3: Start Flask server in background
echo "3️⃣  Starting Flask server..."
echo "   This will seed the database with:"
echo "   - 3 Energy sources (Grid, Solar, Diesel)"
echo "   - 4 Faculties"
echo "   - 12 Buildings"
echo "   - 36 Floors"
echo "   - 1,296 Rooms (Classrooms, Labs, Staff, Smart_Class)"
echo ""
python run.py &
FLASK_PID=$!
echo "   ✓ Flask server started (PID: $FLASK_PID)"
echo ""

# Step 4: Wait for server to be ready
echo "4️⃣  Waiting for server to initialize..."
sleep 5

# Step 5: Check health
echo "5️⃣  Checking server health..."
HEALTH=$(curl -s http://127.0.0.1:5000/api/health)
if [ $? -eq 0 ]; then
    echo "   ✓ Server is healthy!"
    echo ""
    echo "📊 Server Status:"
    echo "$HEALTH" | python -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo "   ⚠️  Server not responding yet, please wait..."
fi

echo ""
echo "✅ Backend is running!"
echo ""
echo "📌 Next Steps:"
echo "   1. In a new terminal, start the dashboard:"
echo "      cd dashboard && npm start"
echo ""
echo "   2. Open browser to: http://localhost:3000"
echo ""
echo "   3. Try the new features:"
echo "      - Energy Flow tab (visual energy flow diagram)"
echo "      - Management tab (add rooms, floors, buildings)"
echo ""
echo "💡 To simulate a power outage:"
echo "   curl -X POST http://127.0.0.1:5000/api/grid-status \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"grid_available\": false, \"reason\": \"Testing\"}'"
echo ""
echo "Press Ctrl+C to stop the Flask server"
echo ""

# Keep script running
wait $FLASK_PID
