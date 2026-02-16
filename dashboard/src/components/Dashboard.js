import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';
import LiveData from './LiveData';
import OptimizationMetrics from './OptimizationMetrics';
import PredictionCard from './PredictionCard';

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchDashboardData, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await dashboardAPI.getLiveDashboard();
      setDashboardData(response.data.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !dashboardData) {
    return <div className="loading">Loading dashboard</div>;
  }

  if (error && !dashboardData) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="dashboard">
      {/* Live Campus Load */}
      <LiveData data={dashboardData?.campus_load} lastUpdated={dashboardData?.last_updated} />
      
      <div className="grid-2">
        {/* Optimization Savings */}
        <OptimizationMetrics data={dashboardData?.optimization_savings} />
        
        {/* Next Hour Prediction */}
        <PredictionCard />
      </div>
    </div>
  );
}

export default Dashboard;
