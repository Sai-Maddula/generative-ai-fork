import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
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

// Auth
export const login = (username, password) =>
  api.post('/auth/login', { username, password });

export const getMe = () => api.get('/auth/me');

// Hierarchy
export const getProvisioningEntities = () => api.get('/provisioning-entities');
export const getOrganizations = (provisioningEntityId = null) =>
  api.get('/organizations', { params: provisioningEntityId ? { provisioning_entity_id: provisioningEntityId } : {} });

// Subscriptions
export const getSubscriptions = (provisioningEntityId = null, organizationId = null, provider = null) => {
  const params = {};
  if (provider) params.provider = provider;
  if (provisioningEntityId !== null) params.provisioning_entity_id = provisioningEntityId;
  if (organizationId !== null) params.organization_id = organizationId;
  return api.get('/subscriptions', { params });
};
export const getSubscription = (id) => api.get(`/subscriptions/${id}`);
export const analyzeSubscription = (id, period = '30d') =>
  api.post(`/subscriptions/${id}/analyze`, { analysis_period: period });

// Recommendations
export const getRecommendations = (provider = null, provisioningEntityId = null, organizationId = null, additionalParams = {}) => {
  const params = { ...additionalParams };
  if (provider) params.provider = provider;
  if (provisioningEntityId !== null) params.provisioning_entity_id = provisioningEntityId;
  if (organizationId !== null) params.organization_id = organizationId;
  return api.get('/recommendations', { params });
};
export const getPendingRecommendations = () =>
  api.get('/recommendations/pending');
export const approveRecommendation = (id) =>
  api.post(`/recommendations/${id}/approve`);
export const rejectRecommendation = (id) =>
  api.post(`/recommendations/${id}/reject`);

// HITL Queue
export const getHITLQueue = (provider = null, provisioningEntityId = null, organizationId = null) => {
  const params = {};
  if (provider) params.provider = provider;
  if (provisioningEntityId !== null) params.provisioning_entity_id = provisioningEntityId;
  if (organizationId !== null) params.organization_id = organizationId;
  return api.get('/hitl/queue', { params });
};
export const submitHITLReview = (analysisId, data) =>
  api.post(`/hitl/review/${analysisId}`, data);

// Forecasting
export const getForecasts = (subId) => api.get(`/forecasts/${subId}`);
export const getAllForecasts = (provider = null, provisioningEntityId = null, organizationId = null) => {
  const params = {};
  if (provider) params.provider = provider;
  if (provisioningEntityId !== null) params.provisioning_entity_id = provisioningEntityId;
  if (organizationId !== null) params.organization_id = organizationId;
  return api.get('/forecasts', { params });
};

// Gamification
export const getLeaderboard = () => api.get('/gamification/leaderboard');
export const getMyStats = () => api.get('/gamification/my-stats');
export const getBadges = () => api.get('/gamification/badges');
export const submitAward = (data) => api.post('/gamification/awards', data);
export const getAwards = () => api.get('/gamification/awards');

// Analytics
export const getCostTrends = (provider = null, provisioningEntityId = null, organizationId = null) => {
  const params = {};
  if (provider) params.provider = provider;
  if (provisioningEntityId !== null) params.provisioning_entity_id = provisioningEntityId;
  if (organizationId !== null) params.organization_id = organizationId;
  return api.get('/analytics/cost-trends', { params });
};
export const getHealthScores = (provisioningEntityId = null, organizationId = null) => {
  const params = {};
  if (provisioningEntityId !== null) params.provisioning_entity_id = provisioningEntityId;
  if (organizationId !== null) params.organization_id = organizationId;
  return api.get('/analytics/health-scores', { params });
};
export const getSummary = (provider = null, provisioningEntityId = null, organizationId = null) => {
  const params = {};
  if (provider) params.provider = provider;
  if (provisioningEntityId !== null) params.provisioning_entity_id = provisioningEntityId;
  if (organizationId !== null) params.organization_id = organizationId;
  return api.get('/analytics/summary', { params });
};

// Analysis Details
export const getAnalysis = (analysisId) => api.get(`/analyses/${analysisId}`);

// Chat
export const sendChatMessage = (message, context = null) =>
  api.post('/chat', { message, context });

export default api;