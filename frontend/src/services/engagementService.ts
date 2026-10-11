import { apiClient } from './api';
import { EngagementRiskSummary, AtRiskCustomer } from '../types/engagement';

// GET /engagement/risk-summary
// Response: { status, message, reference_date, data: [{tier, customer_count, description}] }
export const getRiskSummary = async (): Promise<EngagementRiskSummary> => {
  const res = await apiClient.get('/engagement/risk-summary');
  const body = res.data;
  if (body.status !== 'ok') {
    return { status: body.status, active: 0, cooling: 0, at_risk: 0, inactive: 0, total: 0 };
  }
  const tiers: { tier: string; customer_count: number }[] = body.data ?? [];
  const get = (name: string) => tiers.find((t) => t.tier === name)?.customer_count ?? 0;
  const active = get('Active');
  const cooling = get('Cooling');
  const at_risk = get('At Risk');
  const inactive = get('Inactive');
  return {
    status: 'ok',
    active,
    cooling,
    at_risk,
    inactive,
    total: active + cooling + at_risk + inactive,
  };
};

// GET /engagement/at-risk-customers
// Response: { status, message, total, page, page_size, data: [{customer_unique_id, last_purchase_date, days_since_purchase, tier}] }
export const getAtRiskCustomers = async (
  page: number = 1,
  pageSize: number = 20
): Promise<{ customers: AtRiskCustomer[]; total: number }> => {
  const res = await apiClient.get(`/engagement/at-risk-customers?page=${page}&page_size=${pageSize}`);
  const body = res.data;
  const raw: { customer_unique_id: string; last_purchase_date: string; days_since_purchase: number; tier: string }[] =
    body.data ?? [];
  return {
    customers: raw.map((c) => ({
      customer_id: c.customer_unique_id,
      last_purchase_date: c.last_purchase_date,
      days_since_purchase: c.days_since_purchase,
      total_orders: 0,   // not provided by this endpoint
      total_spent: 0,    // not provided by this endpoint
      risk_tier: c.tier,
    })),
    total: body.total ?? 0,
  };
};
