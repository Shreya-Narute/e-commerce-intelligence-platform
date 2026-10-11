import { apiClient } from './api';
import { CustomerSummary, CustomerState, PurchaseFrequency, CustomerCohort } from '../types/customers';

// GET /customers/summary
// Response: { status, message, data: { total_unique_customers, avg_orders_per_customer, avg_spend_per_customer } }
export const getCustomerSummary = async (): Promise<CustomerSummary> => {
  const res = await apiClient.get('/customers/summary');
  const d = res.data.data ?? {};
  return {
    status: res.data.status,
    total_customers: d.total_unique_customers ?? 0,
    avg_orders_per_customer: d.avg_orders_per_customer ?? 0,
    avg_spend_per_customer: d.avg_spend_per_customer ?? 0,
  };
};

// GET /customers/top-states
// Response: { status, message, data: [{ state, unique_customers }] }
export const getTopStates = async (): Promise<CustomerState[]> => {
  const res = await apiClient.get('/customers/top-states');
  return (res.data.data ?? []).map((item: { state: string; unique_customers: number }) => ({
    state: item.state,
    customer_count: item.unique_customers,
  }));
};

// GET /customers/purchase-frequency
// Response: { status, message, data: [{ order_count, customer_count }] }
export const getPurchaseFrequency = async (): Promise<PurchaseFrequency[]> => {
  const res = await apiClient.get('/customers/purchase-frequency');
  return (res.data.data ?? []).map((item: { order_count: number; customer_count: number }) => ({
    order_count: item.order_count,
    num_customers: item.customer_count,
  }));
};

// GET /customers/cohort
// Response: { status, message, data: [{ cohort_month, new_customers }] }
export const getCohort = async (): Promise<CustomerCohort[]> => {
  const res = await apiClient.get('/customers/cohort');
  return (res.data.data ?? []).map((item: { cohort_month: string; new_customers: number }) => ({
    month: item.cohort_month,
    new_customers: item.new_customers,
  }));
};
