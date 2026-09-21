import axios from 'axios';

// Production: same-origin (empty). Dev: Vite env or localhost:8100
const API_BASE = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:8100' : '');

const api = axios.create({
  baseURL: API_BASE,
});

export const healthAPI = {
  check: () => api.get('/api/health'),
};

export const demoAPI = {
  users: () => api.get('/api/demo/users'),
  reset: () => api.post('/api/demo/reset'),
};

export const authAPI = {
  portals: () => api.get('/api/auth/portals'),
  login: (body) => api.post('/api/auth/login', body),
  me: (token) => api.get('/api/auth/me', { params: { token } }),
};

export const challengesAPI = {
  list: (params) => api.get('/api/challenges', { params }),
  get: (id) => api.get(`/api/challenges/${id}`),
  createJson: (data) => api.post('/api/challenges/json', data),
  createForm: (formData) =>
    api.post('/api/challenges', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  validate: (id, body) => api.post(`/api/challenges/${id}/validate`, body),
  reanalyze: (id) => api.get(`/api/challenges/${id}/reanalyze`),
};

export const projectsAPI = {
  list: (params) => api.get('/api/projects', { params }),
  get: (id) => api.get(`/api/projects/${id}`),
  accept: (challengeId, body) =>
    api.post(`/api/projects/from-challenge/${challengeId}`, body),
  updateTeam: (id, body) => api.put(`/api/projects/${id}/team`, body),
  updateStatus: (id, body) => api.put(`/api/projects/${id}/status`, body),
  addMilestone: (id, body) => api.post(`/api/projects/${id}/milestones`, body),
  updateMilestone: (projectId, milestoneId, body) =>
    api.patch(`/api/projects/${projectId}/milestones/${milestoneId}`, body),
  addCollaboration: (id, body) =>
    api.post(`/api/projects/${id}/collaborations`, body),
  acceptCollaboration: (projectId, collabId) =>
    api.patch(`/api/projects/${projectId}/collaborations/${collabId}/accept`),
  addFeedback: (id, body) => api.post(`/api/projects/${id}/feedback`, body),
  lifecycle: () => api.get('/api/projects/meta/lifecycle'),
};

export const universitiesAPI = {
  list: () => api.get('/api/universities'),
};

export const industryAPI = {
  partners: () => api.get('/api/industry/partners'),
};

export const adminAPI = {
  stats: () => api.get('/api/admin/stats'),
  impact: () => api.get('/api/impact'),
};

export const ragAPI = {
  status: () => api.get('/api/rag/status'),
  query: (body) => api.post('/api/rag/query', body),
  reindex: () => api.post('/api/rag/reindex'),
  documents: () => api.get('/api/rag/documents'),
  addDocument: (body) => api.post('/api/rag/documents', body),
  suggest: (challengeId) => api.get(`/api/rag/suggest/${challengeId}`),
};

export const problemsAPI = {
  analyze: (body) => api.post('/api/problems/analyze', body),
  create: (formData, headers = {}) =>
    api.post('/api/problems', formData, {
      headers: { 'Content-Type': 'multipart/form-data', ...headers },
    }),
  similar: (id) => api.post(`/api/problems/${id}/similar`),
  match: (id) => api.post(`/api/problems/${id}/match`),
  intelligence: (id) => api.get(`/api/problems/${id}/intelligence`),
};

export const speechAPI = {
  transcribe: (formData) =>
    api.post('/api/speech/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

export const projectAIAPI = {
  plan: (id) => api.post(`/api/projects/${id}/plan`),
  approvePlan: (id, body) => api.post(`/api/projects/${id}/plan/approve`, body),
  analyzeFeedback: (id, body) => api.post(`/api/projects/${id}/feedback/analyze`, body),
};

export const dashboardAIAPI = {
  summary: () => api.get('/api/dashboard/ai-summary'),
};

export default api;
