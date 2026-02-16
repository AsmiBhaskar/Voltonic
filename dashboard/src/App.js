import React, { useState, useEffect } from 'react';
import './App.css';
import { dashboardAPI } from './api';
import Dashboard from './components/Dashboard';
import BuildingView from './components/BuildingView';
import AnalyticsCharts from './components/AnalyticsCharts';
import CampusStructure from './components/CampusStructure';
import EnergyFlowDiagram from './components/EnergyFlowDiagram';
import ManagementPanel from './components/ManagementPanel';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [healthStatus, setHealthStatus] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    // Check health on mount
    checkHealth();
    
    // Health check every minute
    const healthInterval = setInterval(checkHealth, 60000);
    
    return () => clearInterval(healthInterval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await dashboardAPI.healthCheck();
      setHealthStatus(response.data);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus({ status: 'error', error: error.message });
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>⚡ VOLTONIC</h1>
          <p className="subtitle">Campus Energy Management System</p>
        </div>
        <div className="header-status">
          <div className={`status-indicator ${healthStatus?.status === 'healthy' ? 'healthy' : 'error'}`}>
            {healthStatus?.status === 'healthy' ? '● Online' : '● Offline'}
          </div>
          {lastUpdate && <span className="last-update">Last update: {lastUpdate}</span>}
        </div>
      </header>

      <nav className="app-nav">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''} 
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={activeTab === 'buildings' ? 'active' : ''} 
          onClick={() => setActiveTab('buildings')}
        >
          🏢 Buildings
        </button>
        <button 
          className={activeTab === 'analytics' ? 'active' : ''} 
          onClick={() => setActiveTab('analytics')}
        >
          📈 Analytics
        </button>
        <button 
          className={activeTab === 'energyflow' ? 'active' : ''} 
          onClick={() => setActiveTab('energyflow')}
        >
          🔋 Energy Flow
        </button>
        <button 
          className={activeTab === 'structure' ? 'active' : ''} 
          onClick={() => setActiveTab('structure')}
        >
          🗺️ Campus Map
        </button>
        <button 
          className={activeTab === 'management' ? 'active' : ''} 
          onClick={() => setActiveTab('management')}
        >
          ⚙️ Management
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'dashboard' && (
          <div className="dashboard-layout">
            <Dashboard />
          </div>
        )}
        
        {activeTab === 'buildings' && (
          <div className="buildings-layout">
            <BuildingView />
          </div>
        )}
        
        {activeTab === 'analytics' && (
          <div className="analytics-layout">
            <AnalyticsCharts />
          </div>
        )}
        
        {activeTab === 'energyflow' && (
          <div className="energyflow-layout">
            <EnergyFlowDiagram />
          </div>
        )}
        
        {activeTab === 'structure' && (
          <div className="structure-layout">
            <CampusStructure />
          </div>
        )}
        
        {activeTab === 'management' && (
          <div className="management-layout">
            <ManagementPanel />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Voltonic Energy Management System - Real-time monitoring & optimization</p>
        {healthStatus && (
          <div className="footer-stats">
            <span>Rooms: {healthStatus.rooms || 0}</span>
            <span>Logs: {healthStatus.logs || 0}</span>
            <span>ML Model: {healthStatus.ml_model || 'unknown'}</span>
          </div>
        )}
      </footer>
    </div>
  );
}

export default App;
