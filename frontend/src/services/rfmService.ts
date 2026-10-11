import { apiClient } from './api';
import { RFMCustomer, RFMSummary, RFMDistributionItem } from '../types/rfm';

// GET /rfm/segments
// Response: { status, message, reference_date, total_customers, silhouette_score, data: RFMSegment[] }
// NOTE: This endpoint triggers heavy computation on cold start (~20-30s). Uses a 60s timeout.
export const getRFMSegments = async (): Promise<RFMSummary> => {
  const res = await apiClient.get('/rfm/segments', { timeout: 60000 });
  const body = res.data;
  return {
    status: body.status,
    message: body.message,
    reference_date: body.reference_date,
    total_customers: body.total_customers,
    silhouette_score: body.silhouette_score,
    segments: body.data ?? [],
  };
};

// GET /rfm/distribution
// Response: { status, message, data: [{ score, r_count, f_count, m_count }] }
export const getRFMDistribution = async (): Promise<RFMDistributionItem[]> => {
  const res = await apiClient.get('/rfm/distribution', { timeout: 60000 });
  return res.data.data ?? [];
};

// GET /rfm/customers?page=&page_size=
// Response: { status, message, total, page, page_size, data: RFMCustomer[] }
export const getRFMCustomers = async (
  page: number = 1,
  pageSize: number = 50
): Promise<{ customers: RFMCustomer[]; total: number }> => {
  const res = await apiClient.get(`/rfm/customers?page=${page}&page_size=${pageSize}`, { timeout: 60000 });
  const body = res.data;
  return {
    customers: body.data ?? [],
    total: body.total ?? 0,
  };
};
