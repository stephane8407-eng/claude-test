/**
 * API Service - Centralized API client with authentication
 * Handles all HTTP requests to the backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors and token refresh
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - logout user
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Authentication API
// ============================================================================

export const authAPI = {
  login: async (email, password) => {
    // Backend expects JSON with email and password fields
    const response = await api.post('/api/auth/login', {
      email,
      password,
    });

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  forgotPassword: async (email) => {
    const response = await api.post('/api/auth/forgot-password', { email });
    return response.data;
  },
};

// ============================================================================
// Village API
// ============================================================================

export const villageAPI = {
  list: async (params = {}) => {
    const response = await api.get('/api/villages/', { params });
    return response.data;
  },

  getBySlug: async (slug) => {
    const response = await api.get(`/api/villages/${slug}`);
    return response.data;
  },

  update: async (slug, data) => {
    const response = await api.put(`/api/villages/${slug}`, data);
    return response.data;
  },

  uploadLogo: async (slug, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(`/api/villages/${slug}/logo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

// ============================================================================
// POI API
// ============================================================================

export const poiAPI = {
  list: async (villageSlug, params = {}) => {
    const response = await api.get(`/api/pois/`, {
      params: { village_slug: villageSlug, ...params }
    });
    return response.data.results || [];
  },

  get: async (villageSlug, poiId) => {
    const response = await api.get(`/api/pois/${poiId}`);
    return response.data;
  },

  create: async (villageSlug, data) => {
    const response = await api.post(`/api/pois/`, data);
    return response.data;
  },

  update: async (villageSlug, poiId, data) => {
    const response = await api.put(`/api/pois/${poiId}`, data);
    return response.data;
  },

  delete: async (villageSlug, poiId) => {
    const response = await api.delete(`/api/pois/${poiId}`);
    return response.data;
  },
};

// ============================================================================
// QR Code API
// ============================================================================

export const qrCodeAPI = {
  list: async (villageSlug) => {
    const response = await api.get(`/api/villages/${villageSlug}/qr-codes`);
    return response.data;
  },

  get: async (villageSlug, qrId) => {
    const response = await api.get(`/api/villages/${villageSlug}/qr-codes/${qrId}`);
    return response.data;
  },

  create: async (villageSlug, data) => {
    const response = await api.post(`/api/villages/${villageSlug}/qr-codes`, data);
    return response.data;
  },

  delete: async (villageSlug, qrId) => {
    const response = await api.delete(`/api/villages/${villageSlug}/qr-codes/${qrId}`);
    return response.data;
  },

  getStats: async (villageSlug, qrId, days = 30) => {
    const response = await api.get(`/api/villages/${villageSlug}/qr-codes/${qrId}/stats`, {
      params: { days },
    });
    return response.data;
  },

  downloadQR: (villageSlug, qrCode, size = 'medium') => {
    return `${API_BASE_URL}/uploads/qr_codes/${villageSlug}/${qrCode}_${size}px.png`;
  },
};

// ============================================================================
// Identity Themes API
// ============================================================================

export const identityAPI = {
  listThemes: async (villageSlug) => {
    const response = await api.get(`/api/villages/${villageSlug}/identity`);
    return response.data;
  },

  generateTheme: async (villageSlug) => {
    const response = await api.post(`/api/villages/${villageSlug}/generate-identity`);
    return response.data;
  },

  // Phase D: Real AI Identity Generation
  generateIdentity: async (villageSlug, auditData, numOptions = 3) => {
    const response = await api.post('/api/identity/generate', {
      village_slug: villageSlug,
      audit_data: auditData,
      num_options: numOptions,
    });
    return response.data;
  },

  generateIdentityPreview: async (villageSlug, auditData, numOptions = 3) => {
    const response = await api.post('/api/identity/generate-preview', {
      village_slug: villageSlug,
      audit_data: auditData,
      num_options: numOptions,
    });
    return response.data;
  },

  getRAGContext: async (villageSlug) => {
    const response = await api.get(`/api/identity/rag-context/${villageSlug}`);
    return response.data;
  },

  getCostEstimate: async () => {
    const response = await api.get('/api/identity/cost-estimate');
    return response.data;
  },

  // Save and publish village identity
  saveIdentity: async (villageSlug, data) => {
    const response = await api.put(`/api/villages/${villageSlug}/identity`, data);
    return response.data;
  },

  // Get published village identity
  getIdentity: async (villageSlug) => {
    const response = await api.get(`/api/villages/${villageSlug}/identity`);
    return response.data;
  },
};

// ============================================================================
// Case Studies API (Phase D)
// ============================================================================

export const caseStudiesAPI = {
  list: async (params = {}) => {
    const response = await api.get('/api/case-studies/', { params });
    return response.data;
  },

  get: async (id) => {
    const response = await api.get(`/api/case-studies/${id}`);
    return response.data;
  },

  create: async (data) => {
    const response = await api.post('/api/case-studies/', data);
    return response.data;
  },

  update: async (id, data) => {
    const response = await api.put(`/api/case-studies/${id}`, data);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/api/case-studies/${id}`);
    return response.data;
  },

  findSimilar: async (params) => {
    const response = await api.post('/api/case-studies/find-similar', params);
    return response.data;
  },

  getFilters: async () => {
    const response = await api.get('/api/case-studies/filters');
    return response.data;
  },
};

// ============================================================================
// Funding Programs API (Phase D)
// ============================================================================

export const fundingAPI = {
  list: async (params = {}) => {
    const response = await api.get('/api/funding-programs/', { params });
    return response.data;
  },

  get: async (id) => {
    const response = await api.get(`/api/funding-programs/${id}`);
    return response.data;
  },

  create: async (data) => {
    const response = await api.post('/api/funding-programs/', data);
    return response.data;
  },

  update: async (id, data) => {
    const response = await api.put(`/api/funding-programs/${id}`, data);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/api/funding-programs/${id}`);
    return response.data;
  },

  match: async (params) => {
    const response = await api.post('/api/funding-programs/match', params);
    return response.data;
  },

  getFilters: async () => {
    const response = await api.get('/api/funding-programs/filters');
    return response.data;
  },
};

// ============================================================================
// Analytics API
// ============================================================================

export const analyticsAPI = {
  getDashboardStats: async (villageSlug) => {
    // Aggregate multiple endpoints for dashboard
    const [pois, qrCodes] = await Promise.all([
      api.get(`/api/pois/`, { params: { village_slug: villageSlug } }),
      api.get(`/api/villages/${villageSlug}/qr-codes`),
    ]);

    // Calculate total scans from all QR codes
    const totalScans = qrCodes.data.reduce((sum, qr) => sum + (qr.scan_count || 0), 0);

    return {
      totalPOIs: pois.data.total || 0,
      totalQRCodes: qrCodes.data.length,
      totalScans,
      recentQRCodes: qrCodes.data.slice(0, 5),
    };
  },

  getQRScanTrends: async (villageSlug, days = 30) => {
    // Get all QR codes and their stats
    const qrCodes = await api.get(`/api/villages/${villageSlug}/qr-codes`);

    const scanData = await Promise.all(
      qrCodes.data.map(qr =>
        api.get(`/api/villages/${villageSlug}/qr-codes/${qr.id}/stats`, {
          params: { days }
        })
      )
    );

    // Aggregate scan data
    const deviceBreakdown = scanData.reduce((acc, { data }) => {
      Object.entries(data.scans_by_device || {}).forEach(([device, count]) => {
        acc[device] = (acc[device] || 0) + count;
      });
      return acc;
    }, {});

    const hourlyBreakdown = scanData.reduce((acc, { data }) => {
      Object.entries(data.scans_by_hour || {}).forEach(([hour, count]) => {
        acc[hour] = (acc[hour] || 0) + count;
      });
      return acc;
    }, {});

    return {
      deviceBreakdown,
      hourlyBreakdown,
      totalScans: Object.values(deviceBreakdown).reduce((a, b) => a + b, 0),
      uniqueVisitors: scanData.reduce((sum, { data }) => sum + (data.unique_visitors || 0), 0),
    };
  },
};

export default api;
