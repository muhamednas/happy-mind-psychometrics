// Thin FastAPI service client for the candidate flow, reports, and chat.
// HR admin data access lives in src/lib/adminApi.js (supabase-js + RLS).
const API_BASE = `${import.meta.env.VITE_API_URL || ''}/api/v1`;

const getAuthHeaders = () => {
  const token = localStorage.getItem('candidateToken');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

const handleResponse = async (response) => {
  if (!response.ok) {
    let errorMessage = 'An error occurred';
    try {
      const errorData = await response.json();
      // FastAPI returns errors under `detail`.
      if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else if (Array.isArray(errorData.detail) && errorData.detail[0]?.msg) {
        errorMessage = errorData.detail[0].msg;
      } else if (errorData.message) {
        errorMessage = errorData.message;
      }
    } catch {
      // non-JSON error body; keep default
    }
    throw new Error(errorMessage);
  }
  return response.json();
};

export const api = {
  candidate: {
    login: async (credentials) => {
      const res = await fetch(`${API_BASE}/candidate/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      return handleResponse(res);
    },
    getDashboard: async () => {
      const res = await fetch(`${API_BASE}/candidate/dashboard`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    getTest: async (assessmentId) => {
      const res = await fetch(`${API_BASE}/candidate/test/${assessmentId}`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    autosave: async (data) => {
      const res = await fetch(`${API_BASE}/candidate/autosave`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(res);
    },
    submitTest: async (assessmentId) => {
      const res = await fetch(`${API_BASE}/candidate/test/${assessmentId}/submit`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      return handleResponse(res);
    },
  },
  chat: {
    sendMessage: async (message) => {
      const res = await fetch(`${API_BASE}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      return handleResponse(res);
    },
  },
};
