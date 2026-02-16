import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

function ManagementPanel() {
  const [activeTab, setActiveTab] = useState('rooms');
  const [faculties, setFaculties] = useState([]);
  const [buildings, setBuildings] = useState([]);
  const [floors, setFloors] = useState([]);
  const [message, setMessage] = useState(null);

  // Room form
  const [roomForm, setRoomForm] = useState({
    name: '',
    type: 'classroom',
    capacity: 40,
    base_load_kw: 0.5,
    floor_id: ''
  });

  // Floor form
  const [floorForm, setFloorForm] = useState({
    number: 1,
    building_id: ''
  });

  // Building form
  const [buildingForm, setBuildingForm] = useState({
    name: '',
    faculty_id: ''
  });

  // Power control
  const [powerControl, setPowerControl] = useState({
    room_id: '',
    action: 'increase',
    value: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [facultiesRes, buildingsRes] = await Promise.all([
        dashboardAPI.getFaculties(),
        dashboardAPI.getBuildings()
      ]);
      
      setFaculties(facultiesRes.data.data);
      setBuildings(buildingsRes.data.data);
      
      // Extract all floors
      const allFloors = [];
      buildingsRes.data.data.forEach(building => {
        building.floors.forEach(floor => {
          allFloors.push({
            ...floor,
            building_name: building.name
          });
        });
      });
      setFloors(allFloors);
    } catch (err) {
      showMessage('Failed to load data', 'error');
    }
  };

  const showMessage = (text, type = 'success') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 4000);
  };

  const handleCreateRoom = async (e) => {
    e.preventDefault();
    try {
      const response = await dashboardAPI.createRoom(roomForm);
      showMessage(`Room ${roomForm.name} created successfully!`, 'success');
      setRoomForm({
        name: '',
        type: 'classroom',
        capacity: 40,
        base_load_kw: 0.5,
        floor_id: ''
      });
      fetchData();
    } catch (err) {
      showMessage(err.response?.data?.message || 'Failed to create room', 'error');
    }
  };

  const handleCreateFloor = async (e) => {
    e.preventDefault();
    try {
      const response = await dashboardAPI.createFloor(floorForm);
      showMessage(`Floor ${floorForm.number} created successfully!`, 'success');
      setFloorForm({ number: 1, building_id: '' });
      fetchData();
    } catch (err) {
      showMessage(err.response?.data?.message || 'Failed to create floor', 'error');
    }
  };

  const handleCreateBuilding = async (e) => {
    e.preventDefault();
    try {
      const response = await dashboardAPI.createBuilding(buildingForm);
      showMessage(`Building ${buildingForm.name} created successfully!`, 'success');
      setBuildingForm({ name: '', faculty_id: '' });
      fetchData();
    } catch (err) {
      showMessage(err.response?.data?.message || 'Failed to create building', 'error');
    }
  };

  const handlePowerControl = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        action: powerControl.action,
        ...(powerControl.action === 'set' && { value: parseFloat(powerControl.value) })
      };
      const response = await dashboardAPI.controlRoomPower(powerControl.room_id, payload);
      showMessage(response.data.message, 'success');
      setPowerControl({ room_id: '', action: 'increase', value: 0 });
    } catch (err) {
      showMessage(err.response?.data?.message || 'Failed to control power', 'error');
    }
  };

  // Get all rooms from floors
  const allRooms = [];
  buildings.forEach(building => {
    building.floors.forEach(floor => {
      floor.rooms?.forEach(room => {
        allRooms.push({
          ...room,
          floor_number: floor.number,
          building_name: building.name
        });
      });
    });
  });

  return (
    <div className="management-panel">
      <h2>⚙️ Campus Management</h2>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="tabs">
        <button
          className={activeTab === 'rooms' ? 'active' : ''}
          onClick={() => setActiveTab('rooms')}
        >
          Add Room
        </button>
        <button
          className={activeTab === 'floors' ? 'active' : ''}
          onClick={() => setActiveTab('floors')}
        >
          Add Floor
        </button>
        <button
          className={activeTab === 'buildings' ? 'active' : ''}
          onClick={() => setActiveTab('buildings')}
        >
          Add Building
        </button>
        <button
          className={activeTab === 'power' ? 'active' : ''}
          onClick={() => setActiveTab('power')}
        >
          Power Control
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'rooms' && (
          <form onSubmit={handleCreateRoom} className="form-section">
            <h3>Create New Room</h3>
            
            <div className="form-group">
              <label>Room Name:</label>
              <input
                type="text"
                value={roomForm.name}
                onChange={(e) => setRoomForm({...roomForm, name: e.target.value})}
                placeholder="e.g., ENG-B1-F1-C31"
                required
              />
            </div>

            <div className="form-group">
              <label>Room Type:</label>
              <select
                value={roomForm.type}
                onChange={(e) => setRoomForm({...roomForm, type: e.target.value})}
              >
                <option value="classroom">Classroom</option>
                <option value="lab">Lab</option>
                <option value="staff">Staff Room</option>
                <option value="Smart_Class">Smart Class</option>
              </select>
            </div>

            <div className="form-group">
              <label>Capacity:</label>
              <input
                type="number"
                value={roomForm.capacity}
                onChange={(e) => setRoomForm({...roomForm, capacity: parseInt(e.target.value)})}
                min="1"
                required
              />
            </div>

            <div className="form-group">
              <label>Base Load (kW):</label>
              <input
                type="number"
                step="0.1"
                value={roomForm.base_load_kw}
                onChange={(e) => setRoomForm({...roomForm, base_load_kw: parseFloat(e.target.value)})}
                min="0.1"
                required
              />
            </div>

            <div className="form-group">
              <label>Floor:</label>
              <select
                value={roomForm.floor_id}
                onChange={(e) => setRoomForm({...roomForm, floor_id: parseInt(e.target.value)})}
                required
              >
                <option value="">Select Floor</option>
                {floors.map(floor => (
                  <option key={floor.id} value={floor.id}>
                    {floor.building_name} - Floor {floor.number}
                  </option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn-primary">Create Room</button>
          </form>
        )}

        {activeTab === 'floors' && (
          <form onSubmit={handleCreateFloor} className="form-section">
            <h3>Create New Floor</h3>
            
            <div className="form-group">
              <label>Floor Number:</label>
              <input
                type="number"
                value={floorForm.number}
                onChange={(e) => setFloorForm({...floorForm, number: parseInt(e.target.value)})}
                min="1"
                required
              />
            </div>

            <div className="form-group">
              <label>Building:</label>
              <select
                value={floorForm.building_id}
                onChange={(e) => setFloorForm({...floorForm, building_id: parseInt(e.target.value)})}
                required
              >
                <option value="">Select Building</option>
                {buildings.map(building => (
                  <option key={building.id} value={building.id}>
                    {building.name} - {building.faculty_name}
                  </option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn-primary">Create Floor</button>
          </form>
        )}

        {activeTab === 'buildings' && (
          <form onSubmit={handleCreateBuilding} className="form-section">
            <h3>Create New Building</h3>
            
            <div className="form-group">
              <label>Building Name:</label>
              <input
                type="text"
                value={buildingForm.name}
                onChange={(e) => setBuildingForm({...buildingForm, name: e.target.value})}
                placeholder="e.g., ENG-B4"
                required
              />
            </div>

            <div className="form-group">
              <label>Faculty:</label>
              <select
                value={buildingForm.faculty_id}
                onChange={(e) => setBuildingForm({...buildingForm, faculty_id: parseInt(e.target.value)})}
                required
              >
                <option value="">Select Faculty</option>
                {faculties.map(faculty => (
                  <option key={faculty.id} value={faculty.id}>
                    {faculty.name}
                  </option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn-primary">Create Building</button>
          </form>
        )}

        {activeTab === 'power' && (
          <form onSubmit={handlePowerControl} className="form-section">
            <h3>Manual Power Control</h3>
            <p className="form-description">
              Adjust power load for specific rooms (for events, extra equipment, etc.)
            </p>
            
            <div className="form-group">
              <label>Select Room:</label>
              <select
                value={powerControl.room_id}
                onChange={(e) => setPowerControl({...powerControl, room_id: parseInt(e.target.value)})}
                required
              >
                <option value="">Select Room</option>
                {allRooms.map((room, idx) => (
                  <option key={idx} value={room.id}>
                    {room.building_name} - Floor {room.floor_number} - {room.type}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Action:</label>
              <select
                value={powerControl.action}
                onChange={(e) => setPowerControl({...powerControl, action: e.target.value})}
              >
                <option value="increase">Increase (+0.5 kW)</option>
                <option value="decrease">Decrease (-0.5 kW)</option>
                <option value="set">Set Custom Value</option>
              </select>
            </div>

            {powerControl.action === 'set' && (
              <div className="form-group">
                <label>Custom Load (kW):</label>
                <input
                  type="number"
                  step="0.1"
                  value={powerControl.value}
                  onChange={(e) => setPowerControl({...powerControl, value: parseFloat(e.target.value)})}
                  min="0.1"
                  required
                />
              </div>
            )}

            <button type="submit" className="btn-primary">Apply Power Control</button>
          </form>
        )}
      </div>

      <style jsx>{`
        .management-panel {
          background: #1e293b;
          border-radius: 8px;
          padding: 20px;
        }

        .management-panel h2 {
          color: #f1f5f9;
          margin: 0 0 20px 0;
        }

        .message {
          padding: 12px 15px;
          border-radius: 6px;
          margin-bottom: 20px;
          font-weight: 500;
        }

        .message.success {
          background: #10b981;
          color: white;
        }

        .message.error {
          background: #ef4444;
          color: white;
        }

        .tabs {
          display: flex;
          gap: 10px;
          margin-bottom: 20px;
          border-bottom: 2px solid #334155;
        }

        .tabs button {
          padding: 10px 20px;
          background: transparent;
          border: none;
          color: #94a3b8;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.2s;
          border-bottom: 2px solid transparent;
          margin-bottom: -2px;
        }

        .tabs button:hover {
          color: #f1f5f9;
        }

        .tabs button.active {
          color: #10b981;
          border-bottom-color: #10b981;
        }

        .tab-content {
          padding: 20px 0;
        }

        .form-section {
          max-width: 600px;
        }

        .form-section h3 {
          color: #f1f5f9;
          margin: 0 0 15px 0;
        }

        .form-description {
          color: #94a3b8;
          font-size: 0.9em;
          margin-bottom: 20px;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-group label {
          display: block;
          color: #cbd5e1;
          margin-bottom: 8px;
          font-weight: 500;
        }

        .form-group input,
        .form-group select {
          width: 100%;
          padding: 10px 12px;
          background: #334155;
          border: 1px solid #475569;
          border-radius: 6px;
          color: #f1f5f9;
          font-size: 14px;
        }

        .form-group input:focus,
        .form-group select:focus {
          outline: none;
          border-color: #10b981;
        }

        .btn-primary {
          padding: 12px 24px;
          background: #10b981;
          color: white;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-primary:hover {
          background: #059669;
        }
      `}</style>
    </div>
  );
}

export default ManagementPanel;
