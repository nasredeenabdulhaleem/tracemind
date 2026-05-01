import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Projects API
export const projectsAPI = {
  list: (params) => api.get('/projects', { params }),
  create: (data) => api.post('/projects', data),
  get: (id) => api.get(`/projects/${id}`),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
};

// Repository API
export const repositoryAPI = {
  uploadZip: (projectId, file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/repository/${projectId}/upload-zip`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress,
    });
  },
  connectGithub: (projectId, data) => api.post(`/repository/${projectId}/connect-github`, data),
  getStatus: (projectId) => api.get(`/repository/${projectId}/repository/status`),
  delete: (projectId) => api.delete(`/repository/${projectId}/repository`),
};

// Parsing API
export const parsingAPI = {
  parse: (projectId) => api.post(`/parsing/${projectId}/parse`),
  getStatus: (projectId) => api.get(`/parsing/${projectId}/parsing-status`),
  deleteChunks: (projectId) => api.delete(`/parsing/${projectId}/chunks`),
};

// Indexing API
export const indexingAPI = {
  createIndex: (projectId) => api.post(`/indexing/${projectId}/index`),
  search: (projectId, data) => api.post(`/indexing/${projectId}/search`, data),
  getStatus: (projectId) => api.get(`/indexing/${projectId}/index/status`),
  deleteIndex: (projectId) => api.delete(`/indexing/${projectId}/index`),
};

// Analysis API
export const analysisAPI = {
  analyze: (data) => api.post('/analysis/analyze', data),
  getHistory: (projectId, params) => api.get(`/analysis/${projectId}/history`, { params }),
  get: (analysisId) => api.get(`/analysis/${analysisId}`),
};

export default api;

// Made with Bob
