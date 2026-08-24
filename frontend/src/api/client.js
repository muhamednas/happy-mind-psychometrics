const BASE_URL = '/api/v1';

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
      errorMessage = errorData.message || errorMessage;
    } catch (e) {
      // JSON parse error, keep default message
    }
    throw new Error(errorMessage);
  }
  return response.json();
};

export const api = {
  admin: {
    createPackage: async (data) => {
      const res = await fetch(`${BASE_URL}/admin/packages/create`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(res);
    },
    getPackages: async () => {
      const res = await fetch(`${BASE_URL}/admin/packages`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    getPackage: async (id) => {
      const res = await fetch(`${BASE_URL}/admin/packages/${id}`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    getCandidates: async () => {
      const res = await fetch(`${BASE_URL}/admin/candidates`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    getCorporates: async () => {
      const res = await fetch(`${BASE_URL}/admin/corporates`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    createCorporate: async (data) => {
      const res = await fetch(`${BASE_URL}/admin/corporates`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(res);
    },
    updateCorporate: async (id, data) => {
      const res = await fetch(`${BASE_URL}/admin/corporates/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(res);
    },
    deleteCorporate: async (id) => {
      const res = await fetch(`${BASE_URL}/admin/corporates/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      return handleResponse(res);
    },
    getCorporateConfig: async (id) => {
      const res = await fetch(`${BASE_URL}/admin/corporates/${id}/config`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    getAssessments: async () => {
      const res = await fetch(`${BASE_URL}/admin/assessments`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    createAssessment: async (data) => {
      const res = await fetch(`${BASE_URL}/admin/assessments`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(res);
    },
    updateAssessment: async (id, data) => {
      const res = await fetch(`${BASE_URL}/admin/assessments/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(res);
    },
    deleteAssessment: async (id) => {
      const res = await fetch(`${BASE_URL}/admin/assessments/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      return handleResponse(res);
    },
    getCandidate: async (id) => {
      const res = await fetch(`${BASE_URL}/admin/candidates/${id}`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    downloadReport: async (candidateId) => {
      const res = await fetch(`${BASE_URL}/admin/candidates/${candidateId}/report`, { headers: getAuthHeaders() });
      if (!res.ok) throw new Error('Failed to download report');
      const blob = await res.blob();
      const contentType = res.headers.get('content-type');
      const isHtml = contentType && contentType.includes('text/html');
      const ext = isHtml ? 'html' : 'pdf';
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report-${candidateId}.${ext}`;
      a.click();
      window.URL.revokeObjectURL(url);
    },
  },
  candidate: {
    login: async (credentials) => {
      const res = await fetch(`${BASE_URL}/candidate/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      return handleResponse(res);
    },
    getDashboard: async () => {
      const res = await fetch(`${BASE_URL}/candidate/dashboard`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    getTest: async (testId) => {
      const res = await fetch(`${BASE_URL}/candidate/test/${testId}`, { headers: getAuthHeaders() });
      return handleResponse(res);
    },
    autosave: async (data) => {
      const res = await fetch(`${BASE_URL}/candidate/autosave`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(res);
    },
    submitTest: async (testId, data) => {
      const res = await fetch(`${BASE_URL}/candidate/test/${testId}/submit`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(res);
    },
  },
  chat: {
    sendMessage: async (message) => {
      const res = await fetch(`${BASE_URL}/chat/message`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ message }),
      });
      return handleResponse(res);
    },
  },
};
