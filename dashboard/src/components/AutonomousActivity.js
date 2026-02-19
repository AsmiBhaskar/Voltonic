import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

function AutonomousActivity() {
  const [logs, setLogs] = useState([]);
  const [summary, setSummary] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [riskySchedules, setRiskySchedules] = useState(null);
  const [accuracy, setAccuracy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('notifications');

  useEffect(() => {
    fetchData();
    
    // Refresh notifications every 30 seconds
    const notifInterval = setInterval(fetchNotifications, 30000);
    
    // Refresh other data every 5 minutes
    const dataInterval = setInterval(fetchData, 300000);

    return () => {
      clearInterval(notifInterval);
      clearInterval(dataInterval);
    };
  }, []);

  const fetchData = async () => {
    try {
      const [logsRes, riskyRes, accuracyRes] = await Promise.all([
        dashboardAPI.getAutonomousLogs(24),
        dashboardAPI.getRiskySchedules(0.5),
        dashboardAPI.getPredictionAccuracy()
      ]);

      if (logsRes.data.status === 'success') {
        setLogs(logsRes.data.data.logs);
        setSummary(logsRes.data.data.summary);
      }
      if (riskyRes.data.status === 'success') {
        setRiskySchedules(riskyRes.data.data);
      }
      if (accuracyRes.data.status === 'success') {
        setAccuracy(accuracyRes.data.data);
      }

      await fetchNotifications();
    } catch (err) {
      console.error('Error fetching autonomous data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchNotifications = async () => {
    try {
      const res = await dashboardAPI.getAutonomousNotifications(10);
      if (res.data.status === 'success') {
        setNotifications(res.data.data.notifications);
      }
    } catch (err) {
      console.error('Error fetching notifications:', err);
    }
  };

  const getDayName = (dayNum) => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days[dayNum] || 'Unknown';
  };

  const getActionColor = (actionType) => {
    switch (actionType) {
      case 'POWER_CUTOFF': return 'var(--accent-yellow)';
      case 'HYBRID_MODE': return 'var(--accent-blue)';
      case 'DEMAND_SPIKE': return 'var(--danger)';
      case 'PREDICTIVE_SWITCH': return 'var(--accent-green)';
      default: return 'var(--text-secondary)';
    }
  };

  const formatTime = (isoString) => {
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="card">
        <div className="loading">Loading autonomous activity...</div>
      </div>
    );
  }

  return (
    <div className="card" style={{ gridColumn: 'span 2' }}>
      <div className="card-header">
        <h2 className="card-title">🤖 Autonomous System Activity</h2>
        {accuracy && accuracy.accuracy !== null && (
          <span className="badge" style={{ 
            background: accuracy.accuracy >= 80 ? 'var(--accent-green)' : 'var(--accent-yellow)',
            color: '#000'
          }}>
            {accuracy.accuracy}% Accuracy
          </span>
        )}
      </div>

      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        {['notifications', 'risky', 'logs'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '0.5rem 1rem',
              background: activeTab === tab ? 'var(--primary)' : 'var(--bg-secondary)',
              color: activeTab === tab ? '#fff' : 'var(--text-secondary)',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: '500'
            }}
          >
            {tab === 'notifications' && '🔔 Notifications'}
            {tab === 'risky' && '⚠️ Risky Schedules'}
            {tab === 'logs' && '📋 Activity Logs'}
          </button>
        ))}
      </div>

      <div className="card-body">
        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div>
            {notifications.length === 0 ? (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
                No recent autonomous actions
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
                {notifications.map((notif) => (
                  <div key={notif.id} style={{
                    padding: '0.75rem 1rem',
                    background: 'var(--bg-secondary)',
                    borderRadius: '8px',
                    borderLeft: `3px solid ${getActionColor(notif.action_type)}`
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '1.2rem' }}>{notif.icon}</span>
                        <span style={{ fontWeight: '500', color: 'var(--text-primary)' }}>
                          {notif.action_type.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {formatTime(notif.timestamp)}
                      </span>
                    </div>
                    <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {notif.message}
                    </div>
                    {(notif.room_name || notif.building_name) && (
                      <div style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {notif.room_name && `Room: ${notif.room_name}`}
                        {notif.building_name && ` • Building: ${notif.building_name}`}
                      </div>
                    )}
                    {notif.energy_saved_kwh > 0 && (
                      <div style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--accent-green)' }}>
                        Energy saved: {notif.energy_saved_kwh.toFixed(3)} kWh
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Risky Schedules Tab */}
        {activeTab === 'risky' && riskySchedules && (
          <div>
            <div style={{ marginBottom: '1rem', padding: '0.75rem', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
                <div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '600', color: 'var(--accent-yellow)' }}>
                    {riskySchedules.rooms_affected}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Affected Rooms</div>
                </div>
                <div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '600', color: 'var(--danger)' }}>
                    {riskySchedules.total_risky_slots}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Risky Slots</div>
                </div>
              </div>
            </div>

            {riskySchedules.rooms_summary.length === 0 ? (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
                No risky schedules detected yet
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '300px', overflowY: 'auto' }}>
                {riskySchedules.rooms_summary.map((room) => (
                  <div key={room.room_id} style={{
                    padding: '0.75rem 1rem',
                    background: 'var(--bg-secondary)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <span style={{ fontWeight: '500', color: 'var(--text-primary)' }}>
                          {room.room_name}
                        </span>
                        <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          ({room.room_type})
                        </span>
                      </div>
                      <span style={{ 
                        padding: '0.25rem 0.5rem', 
                        background: 'var(--danger)', 
                        color: '#fff', 
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: '600'
                      }}>
                        {room.avg_cancellation_rate}% Cancel Rate
                      </span>
                    </div>
                    <div style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {room.high_risk_slots.map((slot, idx) => (
                        <span key={idx} style={{
                          padding: '0.2rem 0.5rem',
                          background: slot.auto_cutoff_enabled ? 'var(--accent-yellow)' : 'var(--bg-tertiary)',
                          color: slot.auto_cutoff_enabled ? '#000' : 'var(--text-secondary)',
                          borderRadius: '4px',
                          fontSize: '0.7rem'
                        }}>
                          {getDayName(slot.day_of_week)} {slot.hour}:00
                          {slot.auto_cutoff_enabled && ' ✓'}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Activity Logs Tab */}
        {activeTab === 'logs' && (
          <div>
            {summary && (
              <div style={{ marginBottom: '1rem', padding: '0.75rem', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
                  <div>
                    <div style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--primary)' }}>
                      {summary.total_actions}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Total Actions</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--accent-green)' }}>
                      {summary.total_energy_saved_kwh.toFixed(2)}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>kWh Saved</div>
                  </div>
                  {Object.entries(summary.action_counts).map(([action, count]) => (
                    <div key={action}>
                      <div style={{ fontSize: '1.25rem', fontWeight: '600', color: getActionColor(action) }}>
                        {count}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                        {action.replace(/_/g, ' ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
              {logs.slice(0, 50).map((log) => (
                <div key={log.id} style={{
                  padding: '0.5rem 0.75rem',
                  background: 'var(--bg-secondary)',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{
                      padding: '0.2rem 0.4rem',
                      background: getActionColor(log.action_type),
                      color: '#000',
                      borderRadius: '4px',
                      fontSize: '0.7rem',
                      fontWeight: '600'
                    }}>
                      {log.action_type}
                    </span>
                    <span style={{ color: 'var(--text-secondary)' }}>
                      {log.room_name || log.building_name || 'System'}
                    </span>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {formatTime(log.timestamp)}
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

export default AutonomousActivity;
