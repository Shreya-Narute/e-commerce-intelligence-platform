import { useState, useEffect, useCallback } from 'react';
import { DataQualityReport } from '../types/dataQuality';
import { dataQualityService } from '../services/dataQualityService';

export const useDataQuality = () => {
  const [data, setData] = useState<DataQualityReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDataQuality = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await dataQualityService.getReport();
      setData(res);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || err.message || 'Failed to fetch data quality report'
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDataQuality();
  }, [fetchDataQuality]);

  return { data, isLoading, error, refetch: fetchDataQuality };
};
