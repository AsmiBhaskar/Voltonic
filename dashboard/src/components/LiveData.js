import React from 'react';

function LiveData({ data, lastUpdated }) {
  if (!data) return null;

  const formatValue = (value) => {
    return typeof value === 'number' ? value.toFixed(2) : value;
  };

  const getLoadStatus = (load) => {
    if (load > 1500) return 'danger';
    if (load > 1200) return 'warning';
    return 'success';
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">⚡ Real-Time Campus Energy</h2>
        <span className="card-icon">🏫</span>
      </div>
      <div className="card-body">
        <div className="metric">
          <div className="metric-label">Total Campus Load</div>
          <div className={`metric-value large ${getLoadStatus(data.total_load_kw)}`}>
            {formatValue(data.total_load_kw)}
            <span className="metric-unit">kW</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(data.total_load_kw / 2000) * 100}%` }}
            />
          </div>
        </div>

        <div className="stats-row">
          <div className="stat-box">
            <div className="stat-box-value">{data.total_rooms}</div>
            <div className="stat-box-label">Total Rooms</div>
          </div>
          <div className="stat-box">
            <div className="stat-box-value">{data.occupied_rooms}</div>
            <div className="stat-box-label">Occupied</div>
          </div>
          <div className="stat-box">
            <div className="stat-box-value">{data.optimized_rooms}</div>
            <div className="stat-box-label">Optimized</div>
          </div>
          <div className="stat-box">
            <div className="stat-box-value">{formatValue(data.avg_temperature)}°C</div>
            <div className="stat-box-label">Avg Temp</div>
          </div>
        </div>

        {lastUpdated && (
          <div style={{ marginTop: '1rem', color: '#64748b', fontSize: '0.85rem' }}>
            Last updated: {new Date(lastUpdated).toLocaleString()}
          </div>
        )}
      </div>
    </div>
  );
}

export default LiveData;
