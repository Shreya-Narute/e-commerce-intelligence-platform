
import { apiClient } from './api';
import {
  SalesSummary,
  MonthlyRevenue,
  RevenueByState,
  RevenueByCategory,
  OrderStatusCount,
  PaymentTypeRevenue,
} from '../types/sales';

export const getSalesSummary = async (): Promise<SalesSummary> => {
  const res = await apiClient.get('/sales/summary');
  const d = res.data.data ?? {};
  return {
    status: res.data.status,
    total_revenue: d.total_revenue ?? 0,
    total_orders: d.total_orders ?? 0,
    avg_order_value: d.average_order_value ?? 0,  // API field: average_order_value
  };
};

export const getMonthlyRevenue = async (): Promise<MonthlyRevenue[]> => {
  const res = await apiClient.get('/sales/monthly');
  return (res.data.data ?? []).map((item: { year_month: string; revenue: number; order_count: number }) => ({
    month: item.year_month,     // API field: year_month
    revenue: item.revenue,
    order_count: item.order_count,
  }));
};

export const getRevenueByState = async (): Promise<RevenueByState[]> => {
  const res = await apiClient.get('/sales/by-state');
  return res.data.data ?? [];
};

export const getRevenueByCategory = async (): Promise<RevenueByCategory[]> => {
  const res = await apiClient.get('/sales/by-category');
  return (res.data.data ?? []).map((item: { category_name: string; revenue: number; order_count: number }) => ({
    category: item.category_name,   // API field: category_name → mapped to category
    revenue: item.revenue,
    order_count: item.order_count,
  }));
};

export const getOrderStatusCounts = async (): Promise<OrderStatusCount[]> => {
  const res = await apiClient.get('/sales/order-status');
  return res.data.data ?? [];
};

export const getPaymentTypeRevenue = async (): Promise<PaymentTypeRevenue[]> => {
  const res = await apiClient.get('/sales/payment-types');
  return res.data.data ?? [];
};
