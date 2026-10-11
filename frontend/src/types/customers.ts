export interface CustomerSummary {
  total_customers: number;
  avg_orders_per_customer: number;
  avg_spend_per_customer: number;
  status: string;
}

export interface CustomerState {
  state: string;
  customer_count: number;
}

export interface PurchaseFrequency {
  order_count: number;
  num_customers: number;
}

export interface CustomerCohort {
  month: string;
  new_customers: number;
}
