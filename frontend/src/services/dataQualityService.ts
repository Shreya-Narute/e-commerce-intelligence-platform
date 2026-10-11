import { apiClient } from './api';
import { DataQualityReport } from '../types/dataQuality';

export const dataQualityService = {
  async getReport(): Promise<DataQualityReport> {
    const response = await apiClient.get<DataQualityReport>('/data-quality');
    return response.data;
  },
};
