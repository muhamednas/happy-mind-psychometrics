import { useState, useEffect, useRef } from 'react';

export function useAutosave(saveFunction, data, delay = 5000) {
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(async () => {
      setIsSaving(true);
      setError(null);
      try {
        await saveFunction(data);
        setLastSaved(new Date());
      } catch (err) {
        setError(err.message || 'Failed to save');
      } finally {
        setIsSaving(false);
      }
    }, delay);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [data, delay, saveFunction]);

  return { isSaving, lastSaved, error };
}
