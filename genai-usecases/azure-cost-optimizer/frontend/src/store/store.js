import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token'),

  setAuth: (user, token) => {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
}));

export const useAppStore = create((set) => ({
  subscriptions: [],
  recommendations: [],
  hitlQueue: [],
  forecasts: [],
  leaderboard: [],
  myStats: null,
  summary: null,
  loading: false,
  error: null,
  analysisInProgress: null,
  lastAnalysisResult: null,
  selectedProvider: localStorage.getItem('selectedProvider') || 'azure',
  provisioningEntities: [],
  organizations: [],
  selectedProvisioningEntity: localStorage.getItem('selectedProvisioningEntity') ? parseInt(localStorage.getItem('selectedProvisioningEntity')) : null,
  selectedOrganization: localStorage.getItem('selectedOrganization') || null,
  selectedSubscription: localStorage.getItem('selectedSubscription') || null,

  setSubscriptions: (subscriptions) => set({ subscriptions }),
  setRecommendations: (recommendations) => set({ recommendations }),
  setHitlQueue: (hitlQueue) => set({ hitlQueue }),
  setForecasts: (forecasts) => set({ forecasts }),
  setLeaderboard: (leaderboard) => set({ leaderboard }),
  setMyStats: (myStats) => set({ myStats }),
  setSummary: (summary) => set({ summary }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setAnalysisInProgress: (analysisInProgress) => set({ analysisInProgress }),
  setLastAnalysisResult: (lastAnalysisResult) => set({ lastAnalysisResult }),
  setSelectedProvider: (provider) => {
    localStorage.setItem('selectedProvider', provider);
    set({ selectedProvider: provider });
  },
  setProvisioningEntities: (provisioningEntities) => set({ provisioningEntities }),
  setOrganizations: (organizations) => set({ organizations }),
  setSelectedProvisioningEntity: (entityId) => {
    if (entityId === null) {
      localStorage.removeItem('selectedProvisioningEntity');
    } else {
      localStorage.setItem('selectedProvisioningEntity', entityId);
    }
    set({ selectedProvisioningEntity: entityId, selectedOrganization: null });
  },
  setSelectedOrganization: (organizationId) => {
    if (organizationId === null) {
      localStorage.removeItem('selectedOrganization');
    } else {
      localStorage.setItem('selectedOrganization', organizationId);
    }
    set({ selectedOrganization: organizationId, selectedSubscription: null });
  },
  setSelectedSubscription: (subscriptionId) => {
    if (subscriptionId === null) {
      localStorage.removeItem('selectedSubscription');
    } else {
      localStorage.setItem('selectedSubscription', subscriptionId);
    }
    set({ selectedSubscription: subscriptionId });
  },
}));