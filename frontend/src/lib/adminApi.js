import { supabase } from './supabaseClient';

const API_BASE = import.meta.env.VITE_API_URL || '';

// HR admin data access via supabase-js. RLS enforces tenant isolation, so these
// queries never need an explicit corporate_id filter.
export const adminApi = {
  async getPackages() {
    const { data, error } = await supabase
      .from('package_overview')
      .select('*')
      .order('created_at', { ascending: false });
    if (error) throw new Error(error.message);
    return data;
  },

  async createPackage({ title, description, tests }) {
    const { data, error } = await supabase.rpc('create_package', {
      p_title: title,
      p_description: description ?? '',
      p_tests: tests ?? [],
    });
    if (error) throw new Error(error.message);
    return data;
  },

  async getCandidates() {
    const { data, error } = await supabase
      .from('candidate_overview')
      .select('*')
      .order('created_at', { ascending: false });
    if (error) throw new Error(error.message);
    return data;
  },

  // Report generation stays in the FastAPI service (WeasyPrint + service_role).
  // We authenticate the request with the HR user's Supabase access token.
  async downloadReport(candidateId) {
    const { data: { session } } = await supabase.auth.getSession();
    const res = await fetch(`${API_BASE}/api/v1/admin/candidates/${candidateId}/report`, {
      headers: { Authorization: `Bearer ${session?.access_token ?? ''}` },
    });
    if (!res.ok) throw new Error('Failed to download report');
    const blob = await res.blob();
    const isHtml = (res.headers.get('content-type') || '').includes('text/html');
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${candidateId}.${isHtml ? 'html' : 'pdf'}`;
    a.click();
    window.URL.revokeObjectURL(url);
  },
};

// Derive a coarse status label from the overview counts.
export function candidateStatus(c) {
  if (c.total_assessments > 0 && c.completed_assessments >= c.total_assessments) return 'completed';
  if (c.completed_assessments > 0 || c.logged_in_at) return 'in_progress';
  return 'not_started';
}
