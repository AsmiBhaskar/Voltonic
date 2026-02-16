import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const dashboardAPI = {
  // Dashboard & Live Data
  getLiveDashboard: () => api.get('/dashboard/live'),
  getCampusLive: () => api.get('/live/campus'),
  getBuildingsLive: () => api.get('/live/buildings'),
  getBuildingLive: (buildingId) => api.get(`/live/building/${buildingId}`),
  
  // Analytics
  getHourlyAnalytics: (hours = 24) => api.get('/analytics/hourly', { params: { hours } }),
  getDailyAnalytics: (days = 7) => api.get('/analytics/daily', { params: { days } }),
  getBuildingComparison: () => api.get('/analytics/building-comparison'),
  
  // Optimization
  getOptimizationSavings: (startTime, endTime) => 
    api.get('/optimization/savings', { params: { start_time: startTime, end_time: endTime } }),
  getOptimizationStatus: () => api.get('/optimization/status'),
  
  // Predictions
  getNextHourPrediction: () => api.get('/prediction/next-hour'),
  trainModel: (hoursBack = 168) => api.post('/prediction/train', { hours_back: hoursBack }),
  getModelInfo: () => api.get('/prediction/model-info'),
  
  // Campus Structure (old endpoints)
  getCampusStructure: () => api.get('/campus/structure'),
  getCampusFaculties: () => api.get('/campus/faculties'),
  getCampusBuildings: () => api.get('/campus/buildings'),
  getRooms: (type, buildingId) => api.get('/campus/rooms', { params: { type, building_id: buildingId } }),
  getRoomDetails: (roomId) => api.get(`/campus/room/${roomId}`),
  
  // Historical Data
  getRoomHistory: (roomId, hours = 24) => api.get(`/history/room/${roomId}`, { params: { hours } }),
  getCampusHistory: (hours = 24) => api.get('/history/campus', { params: { hours } }),
  
  // Statistics
  getStatsSummary: () => api.get('/stats/summary'),
  
  // Health Check
  healthCheck: () => api.get('/health'),
  
  // Energy Sources & Grid Management
  getEnergySources: () => api.get('/energy-sources'),
  getGridStatus: () => api.get('/grid-status'),
  updateGridStatus: (gridAvailable, reason) => 
    api.post('/grid-status', { grid_available: gridAvailable, reason }),
  getEnergyCostBreakdown: (hours = 24) => 
    api.get('/energy-cost-breakdown', { params: { hours } }),
  
  // Building & Room Management
  getBuildings: () => api.get('/buildings'),
  getBuildingEnergyFlow: (buildingId) => api.get(`/buildings/${buildingId}/energy-flow`),
  createRoom: (roomData) => api.post('/rooms', roomData),
  updateRoom: (roomId, roomData) => api.put(`/rooms/${roomId}`, roomData),
  deleteRoom: (roomId) => api.delete(`/rooms/${roomId}`),
  createFloor: (floorData) => api.post('/floors', floorData),
  createBuilding: (buildingData) => api.post('/buildings', buildingData),
  getFaculties: () => api.get('/faculties'),
  
  // Power Control
  controlRoomPower: (roomId, controlData) => 
    api.post(`/rooms/${roomId}/power-control`, controlData),
};

export default api;
