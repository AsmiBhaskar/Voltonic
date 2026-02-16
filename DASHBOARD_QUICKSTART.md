# 🚀 Quick Start Guide - Voltonic Dashboard

Get your Voltonic Energy Management Dashboard up and running in minutes!

## Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- Terminal/Command Prompt

## Option 1: Automated Startup (Recommended - macOS/Linux)

### Single Command
```bash
./start-dashboard.sh
```

This script will:
1. ✓ Start the backend API on port 5000
2. ✓ Install dashboard dependencies (if needed)
3. ✓ Launch the React dashboard on port 3000
4. ✓ Open your browser automatically

Press `Ctrl+C` to stop both services.

---

## Option 2: Manual Startup

### Step 1: Start Backend API
## Start virtual envoirnment file
**Windows:**
```bash
.venv\Scripts\activate
```

```bash
# Install Python dependencies (first time only)
pip install -r requirements.txt

# Start the API server
python run.py
```

The API will be available at: `http://127.0.0.1:5000`

### Step 2: Start Dashboard (in new terminal)

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies (first time only)
npm install

# Start the dashboard
npm start
```

The dashboard will open automatically at: `http://localhost:3000`

---

## 📊 Dashboard Features

### 1. **Main Dashboard Tab**
- Real-time campus energy load
- Total rooms, occupied, and optimized counters
- Average campus temperature
- Optimization savings metrics (energy, cost, CO₂)
- Next hour ML prediction

### 2. **Buildings Tab** 
- Energy consumption by building
- Sorted by highest consumption
- Click any building for details
- Real-time occupancy data

### 3. **Analytics Tab**
- **Hourly Charts**: View 12h, 24h, or 48h trends
- **Daily Summary**: Analyze 7, 14, or 30 day patterns
- **Campus History**: Real-time load, temperature, and optimization tracking

### 4. **Campus Map Tab**
- Browse: Faculties → Buildings → Rooms
- Interactive hierarchy tree
- Click rooms for detailed info
- Visual energy representation

---

## ⚡ Auto-Refresh

All data automatically updates **every 5 seconds** for real-time monitoring.

---

## 🔧 Configuration

### Backend API URL

Default: `http://127.0.0.1:5000/api`

To change, edit `dashboard/package.json`:
```json
"proxy": "http://your-api-url:port"
```

### Refresh Interval

To change auto-refresh rate, edit component files:
```javascript
// dashboard/src/components/*.js
const interval = setInterval(fetchData, 5000); // 5000ms = 5 seconds
```

---

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Get live campus data
curl http://127.0.0.1:5000/api/live/campus

# Run full test suite
python test_api_endpoints.py
```

### Verify Dashboard

1. Open browser to `http://localhost:3000`
2. Check for "● Online" status in header
3. Verify data is loading in all tabs
4. Watch for auto-refresh (numbers should update)

---

## 📚 Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[dashboard/README.md](dashboard/README.md)** - Dashboard detailed guide
- **[dashboard/API_ROUTES_VERIFICATION.md](dashboard/API_ROUTES_VERIFICATION.md)** - Routes verification

---

## 🐛 Troubleshooting

### "Cannot connect to API"
- ✓ Verify backend is running: `curl http://127.0.0.1:5000/api/health`
- ✓ Check for port conflicts (5000 already in use)
- ✓ Look for errors in backend terminal

### "Dashboard not loading"
- ✓ Run `npm install` in dashboard directory
- ✓ Clear npm cache: `npm cache clean --force`
- ✓ Delete `node_modules` and reinstall

### "No data showing"
- ✓ Check if database has data
- ✓ Run: `python -c "from app.models import db, Room; from app import create_app; app = create_app(); app.app_context().push(); print(f'Rooms: {Room.query.count()}')"`
- ✓ Generate test data: `python app/utils/seed_data.py`

### CORS errors
- ✓ Backend should have CORS enabled (already configured)
- ✓ Check browser console for specific errors

---

## 🎯 Next Steps

1. ✓ **Generate Historical Data**
   ```bash
   python app/utils/generate_historical_data.py
   ```

2. ✓ **Train ML Model**
   ```bash
   python app/prediction/train_model.py
   ```

3. ✓ **Start IoT Simulation** (for live data)
   ```bash
   # Already runs automatically when you start the backend
   # Check logs for "IoT Simulator started"
   ```

---

## 🎨 Dashboard Screenshots

Once running, you'll see:

- **Dark themed interface** with real-time metrics
- **Interactive charts** showing energy trends
- **Color-coded status indicators** (green=good, yellow=warning, red=high)
- **Auto-updating counters** every 5 seconds
- **Responsive design** works on desktop and mobile

---

## 💡 Tips

- Keep both terminals open (backend + frontend)
- Use the automated script for easier startup
- Check browser console (F12) for any errors
- Monitor backend terminal for API request logs
- Refresh browser (Cmd/Ctrl + R) if data seems stale

---

## ✅ Verification Checklist

Before using the dashboard, ensure:

- [ ] Python backend running on port 5000
- [ ] Database has rooms and data
- [ ] API health check returns "healthy"
- [ ] Dashboard opens at localhost:3000
- [ ] Header shows "● Online" status
- [ ] Numbers are visible in dashboard cards
- [ ] Charts display data in Analytics tab
- [ ] Buildings list shows in Buildings tab
- [ ] Campus structure loads in Campus Map tab

---

## 🎉 You're All Set!

Your Voltonic Dashboard is now monitoring your campus energy in real-time!

**URLs:**
- Backend API: http://127.0.0.1:5000
- Dashboard: http://localhost:3000
- API Docs: http://127.0.0.1:5000/api/health

For more detailed information, see the full documentation in the `dashboard/` folder.

---

**Need Help?**
- Check `dashboard/README.md` for detailed documentation
- Review `API_DOCUMENTATION.md` for API details
- Look at browser console (F12) for errors
- Check backend terminal for logs
