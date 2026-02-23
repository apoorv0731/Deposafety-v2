// Simple API client for deployed backend
const API_URL = import.meta.env.VITE_API_URL || 'https://deposafety-api.onrender.com';

export const api = {
  health: async () => {
    const res = await fetch(`${API_URL}/health`);
    return res.json();
  },
  
  getProperties: async () => {
    const res = await fetch(`${API_URL}/api/v1/properties`);
    return res.json();
  }
};

export default api;
