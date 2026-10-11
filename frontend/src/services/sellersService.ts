import { apiClient } from './api';
import { SellerSummary, TopSeller, SellerByState, SellerPerformance } from '../types/sellers';

// GET /sellers/summary → { status, message, data: { total_sellers, avg_revenue_per_seller } }
export const getSellerSummary = async (): Promise<SellerSummary> => {
  const res = await apiClient.get('/sellers/summary');
  const d = res.data.data ?? {};
  return {
    status: res.data.status,
    total_sellers: d.total_sellers ?? 0,
    avg_revenue_per_seller: d.avg_revenue_per_seller ?? 0,
    avg_orders_per_seller: 0,  // not provided by this endpoint
  };
};

// GET /sellers/top-revenue → { status, message, data: [{seller_id, seller_state, total_revenue, order_count}] }
export const getTopRevenueSellers = async (): Promise<TopSeller[]> => {
  const res = await apiClient.get('/sellers/top-revenue');
  return (res.data.data ?? []).map((s: { seller_id: string; seller_state: string; total_revenue: number; order_count: number }) => ({
    seller_id: s.seller_id,
    seller_city: '',          // not provided
    seller_state: s.seller_state,
    revenue: s.total_revenue,
    order_count: s.order_count,
    avg_review_score: null,   // not provided by this endpoint
  }));
};

// GET /sellers/by-state → { status, message, data: [{state, seller_count, total_revenue}] }
export const getSellersByState = async (): Promise<SellerByState[]> => {
  const res = await apiClient.get('/sellers/by-state');
  return res.data.data ?? [];
};

// GET /sellers/performance → { status, message, data: [{seller_id, seller_state, avg_review_score, avg_delivery_days, order_count}] }
export const getSellerPerformance = async (): Promise<SellerPerformance[]> => {
  const res = await apiClient.get('/sellers/performance');
  return (res.data.data ?? []).map((s: { seller_id: string; seller_state: string; avg_review_score: number; avg_delivery_days: number; order_count: number }) => ({
    seller_id: s.seller_id,
    avg_delivery_days: s.avg_delivery_days,
    on_time_rate: 0,          // not provided by this endpoint
    avg_review_score: s.avg_review_score,
    order_count: s.order_count,
  }));
};
