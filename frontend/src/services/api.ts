/**
 * API Service
 */
import axios from 'axios';
import { useAuthStore } from '@/store/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE_URL}/api`;

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const { data } = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        localStorage.setItem('token', data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch {
        useAuthStore.getState().logout();
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (email: string, password: string, fullName?: string) =>
    apiClient.post('/auth/register', { email, password, full_name: fullName }),
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  refresh: (token: string) =>
    apiClient.post('/auth/refresh', { refresh_token: token }),
  logout: () => apiClient.post('/auth/logout'),
};

export const predictionsAPI = {
  create: (data: any) => apiClient.post('/predictions', data),
  list: (skip?: number, limit?: number) =>
    apiClient.get('/predictions', { params: { skip, limit } }),
  get: (id: number) => apiClient.get(`/predictions/${id}`),
  delete: (id: number) => apiClient.delete(`/predictions/${id}`),
  getAnalytics: () => apiClient.get('/predictions/stats/analytics'),
};

export const uploadAPI = {
  uploadImage: (predictionId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/upload/images/${predictionId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  deleteImage: (imageId: number) => apiClient.delete(`/upload/images/${imageId}`),
};

export const healthAPI = {
  check: () => apiClient.get('/health'),
};

export default apiClient;
