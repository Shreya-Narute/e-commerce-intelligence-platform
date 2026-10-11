import { useState, useEffect, useCallback } from 'react';
import { HealthResponse } from '../types/health';
import { healthService } from '../services/healthService';

export const useHealth = (pollIntervalMs: number = 30000) => {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = useCallback(async () => {
    try {
      setError(null);
      const res = await healthService.getHealth();
      setData(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Failed to connect to backend server');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, pollIntervalMs);
    return () => clearInterval(interval);
  }, [fetchHealth, pollIntervalMs]);

  return { data, isLoading, error, refetch: fetchHealth };
};
