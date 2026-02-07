import axios from 'axios';

const client = axios.create({
  baseURL: '/api/v1', // Proxy handles redirection to localhost:8000
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add Token to header
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default client;
