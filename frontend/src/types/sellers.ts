export interface SellerSummary {
  total_sellers: number;
  avg_revenue_per_seller: number;
  avg_orders_per_seller: number;
  status: string;
}

export interface TopSeller {
  seller_id: string;
  seller_city: string;
  seller_state: string;
  revenue: number;
  order_count: number;
  avg_review_score: number | null;
}

export interface SellerByState {
  state: string;
  seller_count: number;
  total_revenue: number;
}

export interface SellerPerformance {
  seller_id: string;
  avg_delivery_days: number;
  on_time_rate: number;
  avg_review_score: number;
  order_count: number;
}
