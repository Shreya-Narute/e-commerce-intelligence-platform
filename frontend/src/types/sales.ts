export interface SalesSummary {
  total_revenue: number;
  total_orders: number;
  avg_order_value: number;
  status: string;
}

export interface MonthlyRevenue {
  month: string;
  revenue: number;
  order_count: number;
}

export interface RevenueByState {
  state: string;
  revenue: number;
  order_count: number;
}

export interface RevenueByCategory {
  category: string;
  revenue: number;
  order_count: number;
}

export interface OrderStatusCount {
  status: string;
  count: number;
}

export interface PaymentTypeRevenue {
  payment_type: string;
  revenue: number;
  order_count: number;
}
