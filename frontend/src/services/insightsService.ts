import { apiClient } from './api';
import { InsightsSummary } from '../types/insights';

// GET /insights/summary
// Response: { status, message, insights: [{title, value, context, recommendation, sentiment}] }
// Note: insights is top-level, no .data wrapper
export const getInsightsSummary = async (): Promise<InsightsSummary> => {
  const res = await apiClient.get('/insights/summary');
  return {
    status: res.data.status,
    insights: res.data.insights ?? [],
    generated_at: res.data.generated_at ?? new Date().toISOString(),
  };
};
