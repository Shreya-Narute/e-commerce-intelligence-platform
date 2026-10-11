import { apiClient } from './api';
import { DeliverySummary, DeliveryByState, ReviewDistribution, LateAnalysis } from '../types/delivery';

// GET /delivery/summary → { status, message, data: { avg_delivery_days, on_time_rate, avg_review_score, total_delivered_orders } }
export const getDeliverySummary = async (): Promise<DeliverySummary> => {
  const res = await apiClient.get('/delivery/summary');
  const d = res.data.data ?? {};
  return {
    status: res.data.status,
    avg_delivery_days: d.avg_delivery_days ?? 0,
    on_time_rate: d.on_time_rate ?? 0,
    avg_review_score: d.avg_review_score ?? 0,
    total_orders: d.total_delivered_orders ?? 0,  // field name mapping
  };
};

// GET /delivery/by-state → { status, message, data: [{state, avg_delivery_days, order_count}] }
export const getDeliveryByState = async (): Promise<DeliveryByState[]> => {
  const res = await apiClient.get('/delivery/by-state');
  return res.data.data ?? [];
};

// GET /delivery/review-distribution → { status, message, data: [{review_score, count}] }
export const getReviewDistribution = async (): Promise<ReviewDistribution[]> => {
  const res = await apiClient.get('/delivery/review-distribution');
  return (res.data.data ?? []).map((item: { review_score: number; count: number }) => ({
    score: item.review_score,
    count: item.count,
  }));
};

// GET /delivery/late-analysis → { status, message, data: { on_time_count, late_count, on_time_avg_review, late_avg_review } }
export const getLateAnalysis = async (): Promise<LateAnalysis> => {
  const res = await apiClient.get('/delivery/late-analysis');
  return res.data.data ?? {};
};
