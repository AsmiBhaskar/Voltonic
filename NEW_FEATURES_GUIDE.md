# Voltonic Energy Management - New Features Guide

## Overview
This document describes all the new features added to the Voltonic Energy Management System:

1. **Energy Flow Visualization** - Visual diagram showing energy sources powering each room
2. **Building Management** - Full CRUD operations for rooms, floors, and buildings
3. **Manual Power Control** - Adjust room power loads for events
4. **Comprehensive Room Types** - All 4 room types properly seeded and displayed

---

## 1. Energy Flow Visualization 🔋

### What It Does
- Shows real-time energy flow from sources (Grid/Solar/Diesel) to rooms
- Visualizes which power source is supplying each room
- Displays floor-by-floor breakdown of energy consumption
- Color-coded by energy source
- Interactive navigation through floors

### How to Access
1. Navigate to **Energy Flow** tab in dashboard
2. Select a building from dropdown
3. Click on any floor to expand and see all rooms
4. Each room card shows:
   - Room type (with icon)
   - Current power source (color-coded)
   - Real-time load (kW)
   - Occupancy status
   - Cost per hour
   - Optimization status

### Color Coding
- 🟢 **Green**: Grid electricity ($1/kWh)
- 🟠 **Amber**: Solar+Battery ($0.5/kWh)
- 🔴 **Red**: Diesel generator ($2/kWh)

---

## 2. Management Panel ⚙️

### Features
Located in the **Management** tab, allows full control over:

#### A. Add New Rooms
- Name, type, capacity, base load
- Assign to specific floor
- 4 room types:
  - 📚 Classroom (40-60 capacity, 0.3-0.6 kW base)
  - 🔬 Lab (30-40 capacity, 1.0-2.0 kW base)
  - 👔 Staff Room (5-10 capacity, 0.4-0.8 kW base)
  - 💡 Smart Class (50-80 capacity, 1.5-2.5 kW base)

#### B. Add New Floors
- Create additional floors for any building
- Specify floor number and building

#### C. Add New Buildings
- Create new buildings
- Assign to existing faculty
- Automatically integrated into campus structure

#### D. Manual Power Control
- Adjust room power loads on-the-fly
- Use cases:
  - Special events requiring extra equipment
  - Temporary lab setups
  - Conference rooms
- Actions:
  - **Increase**: +0.5 kW
  - **Decrease**: -0.5 kW
  - **Set Custom**: Specify exact kW value

---

## 3. Room Type Distribution

### Current Campus Structure
- **4 Faculties**: Engineering, Science, Arts, Commerce
- **12 Buildings** (3 per faculty)
- **36 Floors** (3 per building)
- **1,296 Total Rooms**:
  - 1,080 Classrooms
  - 108 Labs
  - 72 Staff Rooms
  - 36 Smart Classes (1 per floor)

### Room Characteristics

| Room Type | Icon | Capacity | Base Load | Equipment Load | Use Case |
|-----------|------|----------|-----------|----------------|----------|
| Classroom | 📚 | 40-60 | 0.3-0.6 kW | 0.2-0.5 kW | Regular lectures |
| Lab | 🔬 | 30-40 | 1.0-2.0 kW | 2.5-4.0 kW | Experiments, research |
| Staff Room | 👔 | 5-10 | 0.4-0.8 kW | 0.3-0.7 kW | Faculty offices |
| Smart Class | 💡 | 50-80 | 1.5-2.5 kW | 3.0-4.5 kW | High-tech lectures |

---

## 4. API Endpoints

### New Endpoints Added

#### Building Management
```
GET  /api/buildings
     Returns all buildings with floor/room structure

GET  /api/buildings/:id/energy-flow
     Real-time energy flow for specific building

POST /api/buildings
     Create new building
     Body: {name, faculty_id}
```

#### Room Management
```
POST /api/rooms
     Create new room
     Body: {name, type, capacity, base_load_kw, floor_id}

PUT  /api/rooms/:id
     Update room details

DELETE /api/rooms/:id
       Delete room
```

#### Floor Management
```
POST /api/floors
     Create new floor
     Body: {number, building_id}
```

#### Power Control
```
POST /api/rooms/:id/power-control
     Manual power adjustment
     Body: {action: "increase|decrease|set", value: 1.5}
```

#### Energy Sources
```
GET  /api/energy-sources
     List all energy sources with costs

GET  /api/grid-status
     Check if grid is online/offline

POST /api/grid-status
     Simulate power outage/restoration
     Body: {grid_available: true/false, reason: "..."}

GET  /api/energy-cost-breakdown?hours=24
     Cost analysis by energy source
```

#### Campus Structure
```
GET /api/faculties
    List all faculties with building counts
```

---

## 5. Energy Source Logic

### Grid Available (Normal Operation)
All rooms powered by **Grid** ($1/kWh)

### Grid Down (Power Outage)
Automatic switchover:
- **Classrooms + Staff Rooms** → Solar+Battery ($0.5/kWh)
- **Labs + Smart Classes** → Diesel Generator ($2/kWh)

### Why This Split?
- Solar has limited capacity - best for lower-load rooms
- Labs and Smart Classes need reliable, high-power source
- Cost optimization while maintaining critical operations

---

## 6. Usage Examples

### Simulate Power Outage
```bash
curl -X POST http://127.0.0.1:5000/api/grid-status \
  -H "Content-Type: application/json" \
  -d '{"grid_available": false, "reason": "Scheduled maintenance"}'
```

### Check Energy Cost Impact
```bash
curl http://127.0.0.1:5000/api/energy-cost-breakdown?hours=1
```

### Add New Room via Dashboard
1. Go to **Management** tab
2. Select "Add Room"
3. Fill form:
   - Name: ENG-B1-F4-C1
   - Type: Smart_Class
   - Capacity: 75
   - Base Load: 2.0
   - Floor: Select from dropdown
4. Click "Create Room"

### Adjust Power for Event
1. Go to **Management** → "Power Control"
2. Select target room
3. Choose action (increase/decrease/set)
4. Apply changes
5. Immediately reflected in Energy Flow diagram

---

## 7. Dashboard Navigation

### Updated Tab Structure
1. **📊 Dashboard** - Overview, live data, predictions
2. **🏢 Buildings** - Building comparison by energy usage
3. **📈 Analytics** - Historical charts and trends
4. **🔋 Energy Flow** - **NEW** Visual energy flow diagram
5. **🗺️ Campus Map** - Hierarchical campus structure
6. **⚙️ Management** - **NEW** Add/manage rooms, floors, buildings

---

## 8. Visual Features

### Energy Flow Diagram
- Building selector dropdown
- Floor accordion (click to expand)
- Room cards with:
  - Type icon
  - Name and type badge
  - Capacity
  - Current load
  - Energy source with color
  - Occupancy indicator
  - Optimization badge
  - Cost calculation
- Auto-refresh every 5 seconds
- Real-time data updates

### Management Panel
- Tabbed interface
- Form validation
- Success/error messages
- Dynamic dropdowns (populated from database)
- Intuitive controls

---

## 9. Testing the Features

### 1. Start Backend
```bash
# Kill existing process on port 5000
lsof -ti:5000 | xargs kill -9

# Delete old database to get fresh seeded data
rm -f instance/voltonic.db

# Start server
python run.py
```

### 2. Start Dashboard
```bash
cd dashboard
npm start
```

### 3. Test Energy Flow
1. Open http://localhost:3000
2. Click **Energy Flow** tab
3. Select different buildings
4. Expand floors to see rooms
5. Observe color-coded energy sources

### 4. Test Management
1. Click **Management** tab
2. Try adding a new room
3. Test power control on existing room
4. Add a new floor to a building

### 5. Simulate Grid Outage
```bash
# Turn off grid
curl -X POST http://127.0.0.1:5000/api/grid-status \
  -H "Content-Type: application/json" \
  -d '{"grid_available": false, "reason": "Testing backup systems"}'

# Watch Energy Flow diagram change colors
# Classrooms → Amber (Solar)
# Labs/Smart_Class → Red (Diesel)

# Restore grid
curl -X POST http://127.0.0.1:5000/api/grid-status \
  -H "Content-Type: application/json" \
  -d '{"grid_available": true}'
```

---

## 10. Data Verification

### Check Room Type Distribution
```bash
curl http://127.0.0.1:5000/api/buildings | python -m json.tool
```

Look for `rooms_by_type` in each floor:
```json
{
  "classroom": 30,
  "lab": 3,
  "staff": 2,
  "Smart_Class": 1
}
```

### Verify Energy Sources
```bash
curl http://127.0.0.1:5000/api/energy-sources | python -m json.tool
```

Should show:
- grid: $1/kWh, priority 1
- solar: $0.5/kWh, priority 2
- diesel: $2/kWh, priority 3

---

## Summary

All requested features have been implemented:

✅ Building data properly represented in API
✅ All 4 room types correctly seeded and distributed
✅ Visual energy flow diagram with source → room visualization
✅ Floor-by-floor navigation
✅ User control over power supply to individual rooms
✅ Dashboard panel to add rooms, floors, buildings, and manage resources
✅ Color-coded energy sources
✅ Real-time updates with auto-refresh
✅ Comprehensive CRUD operations
✅ Grid status management

The system now provides complete visibility and control over campus energy management!
