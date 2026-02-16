import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

function EnergyFlowDiagram() {
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [energyFlow, setEnergyFlow] = useState(null);
  const [selectedFloor, setSelectedFloor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBuildings();
  }, []);

  useEffect(() => {
    if (selectedBuilding) {
      fetchEnergyFlow();
      const interval = setInterval(fetchEnergyFlow, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedBuilding]);

  const fetchBuildings = async () => {
    try {
      const response = await dashboardAPI.getBuildings();
      setBuildings(response.data.data);
      if (response.data.data.length > 0) {
        setSelectedBuilding(response.data.data[0].id);
      }
      setLoading(false);
    } catch (err) {
      setError('Failed to load buildings');
      setLoading(false);
    }
  };

  const fetchEnergyFlow = async () => {
    if (!selectedBuilding) return;
    
    try {
      const response = await dashboardAPI.getBuildingEnergyFlow(selectedBuilding);
      setEnergyFlow(response.data.data);
    } catch (err) {
      console.error('Failed to load energy flow:', err);
    }
  };

  const getSourceColor = (source) => {
    switch(source) {
      case 'grid': return '#10b981'; // green
      case 'solar': return '#f59e0b'; // amber
      case 'diesel': return '#ef4444'; // red
      default: return '#6b7280'; // gray
    }
  };

  const getTypeIcon = (type) => {
    switch(type) {
      case 'classroom': return '📚';
      case 'lab': return '🔬';
      case 'staff': return '👔';
      case 'Smart_Class': return '💡';
      default: return '🏢';
    }
  };

  if (loading) return <div className="loading">Loading energy flow...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!energyFlow) return <div>Select a building to view energy flow</div>;

  const currentBuilding = buildings.find(b => b.id === selectedBuilding);

  return (
    <div className="energy-flow-container">
      <div className="flow-header">
        <h2>🔋 Energy Flow Visualization</h2>
        <div className="building-selector">
          <label>Building: </label>
          <select
            value={selectedBuilding || ''}
            onChange={(e) => setSelectedBuilding(parseInt(e.target.value))}
          >
            {buildings.map(building => (
              <option key={building.id} value={building.id}>
                {building.name} - {building.faculty_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="building-summary">
        <div className="summary-card">
          <h4>{energyFlow.building_name}</h4>
          <p>Total Load: <strong>{energyFlow.total_load.toFixed(2)} kW</strong></p>
          <p>Floors: {energyFlow.floors.length}</p>
          <p className="timestamp">Updated: {new Date(energyFlow.timestamp).toLocaleTimeString()}</p>
        </div>
      </div>

      <div className="energy-sources-legend">
        <h4>Energy Sources:</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color" style={{backgroundColor: '#10b981'}}></span>
            <span>Grid ($1/kWh)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{backgroundColor: '#f59e0b'}}></span>
            <span>Solar ($0.5/kWh)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{backgroundColor: '#ef4444'}}></span>
            <span>Diesel ($2/kWh)</span>
          </div>
        </div>
      </div>

      <div className="floors-container">
        {energyFlow.floors.map(floor => (
          <div key={floor.floor_id} className="floor-section">
            <div 
              className="floor-header"
              onClick={() => setSelectedFloor(selectedFloor === floor.floor_id ? null : floor.floor_id)}
            >
              <h3>
                Floor {floor.floor_number}
                <span className="floor-load">{floor.total_load.toFixed(2)} kW</span>
              </h3>
              <span className="expand-icon">{selectedFloor === floor.floor_id ? '▼' : '▶'}</span>
            </div>

            {selectedFloor === floor.floor_id && (
              <div className="rooms-grid">
                {floor.rooms.map(room => (
                  <div 
                    key={room.room_id} 
                    className={`room-card ${room.occupancy ? 'occupied' : 'vacant'}`}
                    style={{
                      borderLeft: `4px solid ${getSourceColor(room.energy_source)}`
                    }}
                  >
                    <div className="room-header">
                      <span className="room-icon">{getTypeIcon(room.room_type)}</span>
                      <span className="room-name">{room.room_name}</span>
                    </div>
                    
                    <div className="room-details">
                      <div className="detail-row">
                        <span>Type:</span>
                        <span className="room-type-badge">{room.room_type}</span>
                      </div>
                      <div className="detail-row">
                        <span>Capacity:</span>
                        <span>{room.capacity}</span>
                      </div>
                      <div className="detail-row">
                        <span>Load:</span>
                        <span className="load-value">{room.total_load.toFixed(2)} kW</span>
                      </div>
                      <div className="detail-row">
                        <span>Source:</span>
                        <span 
                          className="source-badge"
                          style={{
                            backgroundColor: getSourceColor(room.energy_source),
                            color: 'white',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            fontSize: '0.85em'
                          }}
                        >
                          {room.energy_source}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span>Status:</span>
                        <span className={room.occupancy ? 'status-active' : 'status-idle'}>
                          {room.occupancy ? '✓ Occupied' : '○ Vacant'}
                        </span>
                      </div>
                      {room.optimized && (
                        <div className="optimized-badge">⚡ Optimized</div>
                      )}
                    </div>

                    <div className="energy-flow-arrow">
                      <div className="arrow">→</div>
                      <div className="flow-label">${(room.total_load * room.energy_source_cost).toFixed(2)}/h</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <style jsx>{`
        .energy-flow-container {
          padding: 20px;
          background: #1e293b;
          border-radius: 8px;
        }

        .flow-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .flow-header h2 {
          color: #f1f5f9;
          margin: 0;
        }

        .building-selector {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .building-selector label {
          color: #94a3b8;
        }

        .building-selector select {
          padding: 8px 12px;
          background: #334155;
          border: 1px solid #475569;
          border-radius: 4px;
          color: #f1f5f9;
          font-size: 14px;
        }

        .building-summary {
          background: #334155;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .summary-card h4 {
          color: #f1f5f9;
          margin: 0 0 10px 0;
        }

        .summary-card p {
          color: #94a3b8;
          margin: 5px 0;
        }

        .summary-card strong {
          color: #10b981;
          font-size: 1.1em;
        }

        .timestamp {
          font-size: 0.85em;
          color: #64748b;
        }

        .energy-sources-legend {
          background: #334155;
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .energy-sources-legend h4 {
          color: #f1f5f9;
          margin: 0 0 10px 0;
        }

        .legend-items {
          display: flex;
          gap: 20px;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #94a3b8;
        }

        .legend-color {
          width: 20px;
          height: 20px;
          border-radius: 4px;
        }

        .floors-container {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .floor-section {
          background: #334155;
          border-radius: 8px;
          overflow: hidden;
        }

        .floor-header {
          padding: 15px 20px;
          background: #475569;
          cursor: pointer;
          display: flex;
          justify-content: space-between;
          align-items: center;
          user-select: none;
        }

        .floor-header:hover {
          background: #526479;
        }

        .floor-header h3 {
          color: #f1f5f9;
          margin: 0;
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .floor-load {
          font-size: 0.9em;
          color: #10b981;
          font-weight: normal;
        }

        .expand-icon {
          color: #94a3b8;
        }

        .rooms-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 15px;
          padding: 20px;
        }

        .room-card {
          background: #1e293b;
          border-radius: 8px;
          padding: 15px;
          transition: transform 0.2s;
        }

        .room-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .room-card.occupied {
          background: #1f3a2e;
        }

        .room-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
        }

        .room-icon {
          font-size: 1.5em;
        }

        .room-name {
          color: #f1f5f9;
          font-weight: 500;
          font-size: 0.9em;
        }

        .room-details {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .detail-row {
          display: flex;
          justify-content: space-between;
          font-size: 0.85em;
          color: #94a3b8;
        }

        .room-type-badge {
          background: #475569;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 0.9em;
          color: #e2e8f0;
        }

        .load-value {
          color: #10b981;
          font-weight: 600;
        }

        .status-active {
          color: #10b981;
        }

        .status-idle {
          color: #64748b;
        }

        .optimized-badge {
          background: #10b981;
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 0.75em;
          text-align: center;
          margin-top: 8px;
        }

        .energy-flow-arrow {
          margin-top: 10px;
          padding-top: 10px;
          border-top: 1px solid #475569;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 5px;
        }

        .arrow {
          color: #10b981;
          font-size: 1.2em;
        }

        .flow-label {
          color: #f59e0b;
          font-weight: 600;
          font-size: 0.9em;
        }

        .loading, .error {
          padding: 40px;
          text-align: center;
          color: #94a3b8;
        }

        .error {
          color: #ef4444;
        }
      `}</style>
    </div>
  );
}

export default EnergyFlowDiagram;
