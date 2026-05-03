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
      // Don't redirect if the 401 came from the auth endpoints themselves
      const url = error.config?.url || '';
      const isAuthRoute = url.includes('/auth/login') || url.includes('/auth/register');
      if (!isAuthRoute) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
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
  connectGithub: (projectId, repoUrl) => {
    const formData = new FormData();
    formData.append('repo_url', repoUrl);
    return api.post(`/repository/${projectId}/connect-github`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
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
  analyzeStream: (data, onEvent) => {
    // Returns a controller so the caller can abort
    const controller = new AbortController();
    const token = localStorage.getItem('token');
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

    fetch(`${baseUrl}/analysis/analyze/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(data),
      signal: controller.signal,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
        onEvent({ type: 'error', message: err.detail || 'Analysis failed' });
        return;
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // keep incomplete line
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              onEvent(event);
            } catch {/* ignore malformed */}
          }
        }
      }
    }).catch((err) => {
      if (err.name !== 'AbortError') {
        onEvent({ type: 'error', message: err.message || 'Stream error' });
      }
    });

    return controller;
  },
  getHistory: (projectId, params) => api.get(`/analysis/${projectId}/history`, { params }),
  get: (analysisId) => api.get(`/analysis/${analysisId}`),
};

export default api;

// Made with Bob
