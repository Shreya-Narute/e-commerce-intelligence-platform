export interface DeliverySummary {
  avg_delivery_days: number;
  on_time_rate: number;
  avg_review_score: number;
  total_orders: number;   // mapped from total_delivered_orders
  status: string;
}

export interface DeliveryByState {
  state: string;
  avg_delivery_days: number;
  order_count: number;
}

export interface ReviewDistribution {
  score: number;
  count: number;
}

// API returns a dict, not an array
export interface LateAnalysis {
  on_time_count: number;
  late_count: number;
  on_time_avg_review: number;
  late_avg_review: number;
}
