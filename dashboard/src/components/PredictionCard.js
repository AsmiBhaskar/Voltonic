import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

function PredictionCard() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPrediction();
    
    // Refresh prediction every 5 seconds
    const interval = setInterval(fetchPrediction, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchPrediction = async () => {
    try {
      const response = await dashboardAPI.getNextHourPrediction();
      setPrediction(response.data.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching prediction:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !prediction) {
    return (
      <div className="card">
        <div className="loading">Loading prediction</div>
      </div>
    );
  }

  if (error && !prediction) {
    return (
      <div className="card">
        <div className="error">Prediction unavailable: {error}</div>
      </div>
    );
  }

  const getDifference = () => {
    const diff = prediction.predicted_load_kw - prediction.current_load_kw;
    const percentage = ((diff / prediction.current_load_kw) * 100).toFixed(1);
    return { diff: diff.toFixed(2), percentage };
  };

  const { diff, percentage } = getDifference();
  const isIncrease = diff > 0;

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">🔮 Next Hour Prediction</h2>
        <span className="badge info">ML Powered</span>
      </div>
      <div className="card-body">
        <div className="metric">
          <div className="metric-label">Predicted Load</div>
          <div className="metric-value large">
            {prediction.predicted_load_kw.toFixed(2)}
            <span className="metric-unit">kW</span>
          </div>
        </div>

        <div className="stats-row" style={{ marginTop: '1rem' }}>
          <div className="stat-box">
            <div className="stat-box-value">{prediction.current_load_kw.toFixed(2)}</div>
            <div className="stat-box-label">Current Load</div>
          </div>
          <div className="stat-box">
            <div className={`stat-box-value ${isIncrease ? 'danger' : 'success'}`}>
              {isIncrease ? '↑' : '↓'} {percentage}%
            </div>
            <div className="stat-box-label">Change</div>
          </div>
        </div>

        {prediction.confidence_interval && (
          <div style={{ marginTop: '1rem', color: '#94a3b8', fontSize: '0.85rem' }}>
            <div>Confidence Interval:</div>
            <div style={{ color: '#cbd5e1' }}>
              {prediction.confidence_interval.lower.toFixed(2)} - {prediction.confidence_interval.upper.toFixed(2)} kW
            </div>
          </div>
        )}

        {prediction.prediction_for && (
          <div style={{ marginTop: '0.5rem', color: '#64748b', fontSize: '0.85rem' }}>
            For: {new Date(prediction.prediction_for).toLocaleString()}
          </div>
        )}
      </div>
    </div>
  );
}

export default PredictionCard;
