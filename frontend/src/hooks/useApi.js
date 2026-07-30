import { useState, useCallback } from 'react';

export function useApi() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiFunction, ...args) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction(...args);
      setData(result);
      return { success: true, data: result };
    } catch (err) {
      setError(err.message || 'An error occurred');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, execute };
}
