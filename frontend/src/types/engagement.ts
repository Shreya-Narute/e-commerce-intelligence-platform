export interface EngagementRiskSummary {
  active: number;
  cooling: number;
  at_risk: number;
  inactive: number;
  total: number;
  status: string;
}

export interface AtRiskCustomer {
  customer_id: string;           // mapped from customer_unique_id
  last_purchase_date: string;
  days_since_purchase: number;
  total_orders: number;          // 0 — not provided by the endpoint
  total_spent: number;           // 0 — not provided by the endpoint
  risk_tier: string;             // mapped from tier
}
