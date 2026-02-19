import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

function SolarStatus() {
  const [solarStatus, setSolarStatus] = useState(null);
  const [hybridStatus, setHybridStatus] = useState(null);
  const [prediction30, setPrediction30] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
    
    // Refresh every 2 minutes
    const interval = setInterval(fetchData, 120000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [solarRes, hybridRes, predRes] = await Promise.all([
        dashboardAPI.getSolarStatus(),
        dashboardAPI.getHybridStatus(),
        dashboardAPI.get30MinPrediction()
      ]);

      if (solarRes.data.status === 'success') {
        setSolarStatus(solarRes.data.data);
      }
      if (hybridRes.data.status === 'success') {
        setHybridStatus(hybridRes.data.data);
      }
      if (predRes.data.status === 'success') {
        setPrediction30(predRes.data.data);
      }
      setError(null);
    } catch (err) {
      console.error('Error fetching solar status:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSolarIcon = () => {
    if (!solarStatus) return '☀️';
    if (solarStatus.is_night) return '🌙';
    if (solarStatus.is_evening) return '🌅';
    return '☀️';
  };

  const getSolarColor = () => {
    if (!solarStatus) return 'var(--text-secondary)';
    if (solarStatus.solar_availability_factor === 1) return 'var(--accent-yellow)';
    if (solarStatus.solar_availability_factor > 0) return 'var(--accent-orange)';
    return 'var(--text-muted)';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return '📈';
    if (trend === 'decreasing') return '📉';
    return '➡️';
  };

  if (loading) {
    return (
      <div className="card">
        <div className="loading">Loading solar status...</div>
      </div>
    );
  }

  if (error && !solarStatus) {
    return (
      <div className="card">
        <div className="error">Solar status unavailable</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          {getSolarIcon()} Power Status
        </h2>
        {hybridStatus && hybridStatus.hybrid_buildings_count > 0 && (
          <span className="badge" style={{ background: 'var(--accent-blue)', color: '#fff' }}>
            Hybrid Active
          </span>
        )}
      </div>

      <div className="card-body">
        {/* Solar Availability */}
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Solar Availability</span>
            <span style={{ 
              fontSize: '1.25rem', 
              fontWeight: '600', 
              color: getSolarColor() 
            }}>
              {solarStatus ? Math.round(solarStatus.solar_availability_factor * 100) : 0}%
            </span>
          </div>
          
          {/* Progress bar */}
          <div style={{
            height: '8px',
            background: 'var(--bg-secondary)',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${solarStatus ? solarStatus.solar_availability_factor * 100 : 0}%`,
              background: getSolarColor(),
              borderRadius: '4px',
              transition: 'width 0.5s ease'
            }} />
          </div>
          
          <div style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {solarStatus?.is_peak_solar && 'Peak solar hours (6 AM - 6 PM)'}
            {solarStatus?.is_evening && 'Evening mode - reduced solar capacity'}
            {solarStatus?.is_night && 'Night mode - grid powered'}
          </div>
        </div>

        {/* 30-Min Prediction */}
        {prediction30 && (
          <div style={{
            padding: '0.75rem',
            background: 'var(--bg-secondary)',
            borderRadius: '8px',
            marginBottom: '1rem'
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '0.5rem'
            }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                30-Min Prediction
              </span>
              <span style={{ fontSize: '1rem' }}>{getTrendIcon(prediction30.trend)}</span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <div>
                <span style={{ fontSize: '1.5rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                  {prediction30.predicted_load_kw}
                </span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginLeft: '0.25rem' }}>kW</span>
              </div>
              <div style={{
                color: prediction30.load_change_kw > 0 ? 'var(--danger)' : 'var(--accent-green)',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}>
                {prediction30.load_change_kw > 0 ? '+' : ''}{prediction30.load_change_kw} kW
              </div>
            </div>
            
            <div style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Trend: {prediction30.trend}
            </div>
          </div>
        )}

        {/* Hybrid Mode Buildings */}
        {hybridStatus && hybridStatus.hybrid_buildings_count > 0 && (
          <div>
            <div style={{ 
              fontSize: '0.75rem', 
              color: 'var(--text-muted)', 
              textTransform: 'uppercase',
              marginBottom: '0.5rem'
            }}>
              Hybrid Mode Active ({hybridStatus.hybrid_buildings_count} buildings)
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {hybridStatus.buildings.map((building) => (
                <div key={building.building_id} style={{
                  padding: '0.5rem',
                  background: 'var(--bg-tertiary)',
                  borderRadius: '6px',
                  fontSize: '0.85rem'
                }}>
                  <div style={{ fontWeight: '500', color: 'var(--text-primary)' }}>
                    {building.building_name}
                  </div>
                  <div style={{ 
                    display: 'flex', 
                    gap: '1rem', 
                    marginTop: '0.25rem',
                    fontSize: '0.75rem'
                  }}>
                    <span style={{ color: 'var(--accent-yellow)' }}>
                      ☀️ {building.solar_output_kw} kW
                    </span>
                    <span style={{ color: 'var(--accent-blue)' }}>
                      ⚡ Grid backup
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Building Solar Capacities */}
        {solarStatus?.buildings && solarStatus.buildings.length > 0 && !hybridStatus?.hybrid_buildings_count && (
          <div>
            <div style={{ 
              fontSize: '0.75rem', 
              color: 'var(--text-muted)', 
              textTransform: 'uppercase',
              marginBottom: '0.5rem'
            }}>
              Building Stats
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '150px', overflowY: 'auto' }}>
              {solarStatus.buildings.slice(0, 5).map((building) => (
                <div key={building.building_id} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.4rem 0.5rem',
                  background: 'var(--bg-tertiary)',
                  borderRadius: '4px',
                  fontSize: '0.8rem'
                }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{building.building_name}</span>
                  <span style={{ color: 'var(--accent-yellow)', fontWeight: '500' }}>
                    {building.effective_capacity_kw} kW
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SolarStatus;
