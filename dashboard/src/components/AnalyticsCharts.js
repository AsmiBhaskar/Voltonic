import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

function AnalyticsCharts() {
  const [hourlyData, setHourlyData] = useState([]);
  const [dailyData, setDailyData] = useState([]);
  const [campusHistory, setCampusHistory] = useState([]);
  const [timeRange, setTimeRange] = useState({ hourly: 24, daily: 7, history: 24 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAllData();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchAllData, 5000);
    
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchAllData = async () => {
    try {
      const [hourlyRes, dailyRes, historyRes] = await Promise.all([
        dashboardAPI.getHourlyAnalytics(timeRange.hourly),
        dashboardAPI.getDailyAnalytics(timeRange.daily),
        dashboardAPI.getCampusHistory(timeRange.history)
      ]);

      setHourlyData(hourlyRes.data.data || []);
      setDailyData(dailyRes.data.data || []);
      setCampusHistory(historyRes.data.data || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && hourlyData.length === 0) {
    return <div className="loading">Loading analytics</div>;
  }

  if (error && hourlyData.length === 0) {
    return <div className="error">Error: {error}</div>;
  }

  const formatHourlyData = () => {
    return hourlyData.map(item => ({
      time: new Date(item.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      consumption: parseFloat(item.total_consumption_kwh?.toFixed(2) || 0),
      avgLoad: parseFloat(item.avg_load_kw?.toFixed(2) || 0),
      maxLoad: parseFloat(item.max_load_kw?.toFixed(2) || 0)
    })).reverse();
  };

  const formatDailyData = () => {
    return dailyData.map(item => ({
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      consumption: parseFloat(item.total_consumption_kwh?.toFixed(2) || 0),
      avgLoad: parseFloat(item.avg_load_kw?.toFixed(2) || 0),
      peakLoad: parseFloat(item.peak_load_kw?.toFixed(2) || 0)
    })).reverse();
  };

  const formatCampusHistory = () => {
    return campusHistory.map(item => ({
      time: new Date(item.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      load: parseFloat(item.total_load_kw?.toFixed(2) || 0),
      temperature: parseFloat(item.avg_temperature?.toFixed(1) || 0),
      occupied: item.occupied_rooms || 0,
      optimized: item.optimized_rooms || 0
    })).reverse();
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '8px',
          padding: '0.75rem',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
        }}>
          <p style={{ color: '#cbd5e1', marginBottom: '0.5rem', fontWeight: 600 }}>{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color, margin: '0.25rem 0' }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="analytics-view">
      {/* Hourly Consumption */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📊 Hourly Energy Consumption</h2>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button 
              className={`btn ${timeRange.hourly === 12 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange({...timeRange, hourly: 12})}
            >
              12h
            </button>
            <button 
              className={`btn ${timeRange.hourly === 24 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange({...timeRange, hourly: 24})}
            >
              24h
            </button>
            <button 
              className={`btn ${timeRange.hourly === 48 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange({...timeRange, hourly: 48})}
            >
              48h
            </button>
          </div>
        </div>
        <div className="card-body">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={formatHourlyData()}>
              <defs>
                <linearGradient id="colorConsumption" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ color: '#cbd5e1' }} />
              <Area 
                type="monotone" 
                dataKey="consumption" 
                stroke="#3b82f6" 
                fillOpacity={1} 
                fill="url(#colorConsumption)" 
                name="Consumption (kWh)"
              />
              <Line type="monotone" dataKey="avgLoad" stroke="#10b981" name="Avg Load (kW)" />
              <Line type="monotone" dataKey="maxLoad" stroke="#ef4444" name="Max Load (kW)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Daily Summary */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header">
          <h2 className="card-title">📈 Daily Energy Summary</h2>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button 
              className={`btn ${timeRange.daily === 7 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange({...timeRange, daily: 7})}
            >
              7 days
            </button>
            <button 
              className={`btn ${timeRange.daily === 14 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange({...timeRange, daily: 14})}
            >
              14 days
            </button>
            <button 
              className={`btn ${timeRange.daily === 30 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange({...timeRange, daily: 30})}
            >
              30 days
            </button>
          </div>
        </div>
        <div className="card-body">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={formatDailyData()}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ color: '#cbd5e1' }} />
              <Bar dataKey="consumption" fill="#3b82f6" name="Total Consumption (kWh)" />
              <Bar dataKey="peakLoad" fill="#f59e0b" name="Peak Load (kW)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Campus History */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header">
          <h2 className="card-title">🏫 Campus Load History</h2>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button 
              className={`btn ${timeRange.history === 6 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange({...timeRange, history: 6})}
            >
              6h
            </button>
            <button 
              className={`btn ${timeRange.history === 24 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange({...timeRange, history: 24})}
            >
              24h
            </button>
          </div>
        </div>
        <div className="card-body">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={formatCampusHistory()}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#94a3b8" />
              <YAxis yAxisId="left" stroke="#94a3b8" />
              <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ color: '#cbd5e1' }} />
              <Line yAxisId="left" type="monotone" dataKey="load" stroke="#3b82f6" strokeWidth={2} name="Total Load (kW)" />
              <Line yAxisId="right" type="monotone" dataKey="temperature" stroke="#f59e0b" name="Avg Temp (°C)" />
              <Line yAxisId="right" type="monotone" dataKey="occupied" stroke="#10b981" name="Occupied Rooms" />
              <Line yAxisId="right" type="monotone" dataKey="optimized" stroke="#8b5cf6" name="Optimized Rooms" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsCharts;
