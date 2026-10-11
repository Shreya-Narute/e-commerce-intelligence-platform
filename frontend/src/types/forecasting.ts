// Matches /forecasting/revenue and /forecasting/orders response
// API: { status, message, metric, mae, rmse, mape, forecast:[{period,forecast,lower_bound,upper_bound}], historical:[{period,value}] }

export interface ForecastPoint {
  period: string;          // API field name (not "month")
  forecast: number;
  lower_bound?: number;
  upper_bound?: number;
}

export interface HistoricalPoint {
  period: string;
  value: number;
}

export interface ForecastResult {
  status: string;
  message?: string;
  metric?: string;
  mae: number | null;
  rmse: number | null;
  mape: number | null;
  forecast: ForecastPoint[];
  historical: HistoricalPoint[];
}
