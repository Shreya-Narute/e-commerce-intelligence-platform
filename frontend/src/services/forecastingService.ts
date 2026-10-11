import { apiClient } from './api';
import { ForecastResult } from '../types/forecasting';

// GET /forecasting/revenue and /forecasting/orders
// Response: { status, message, metric, mae, rmse, mape, forecast:[...], historical:[...] }
// Note: top-level object — no .data wrapper for this endpoint family
export const getRevenueForecast = async (): Promise<ForecastResult> => {
  const res = await apiClient.get('/forecasting/revenue');
  return res.data;
};

export const getOrderForecast = async (): Promise<ForecastResult> => {
  const res = await apiClient.get('/forecasting/orders');
  return res.data;
};
