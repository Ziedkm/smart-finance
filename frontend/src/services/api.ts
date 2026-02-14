import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add auth token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle errors gracefully for demo mode)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect to login for demo mode
    // Just log the error and let the component handle it
    console.warn('API Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);
