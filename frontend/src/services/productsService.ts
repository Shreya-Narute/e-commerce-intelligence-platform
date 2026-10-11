import { apiClient } from './api';
import { ProductRevenue, CategoryStats, CategoryTrend, ProductDimensions } from '../types/products';

// GET /products/top-revenue → { status, message, data: [{product_id, category_name, revenue, order_count}] }
export const getTopRevenueProducts = async (): Promise<ProductRevenue[]> => {
  const res = await apiClient.get('/products/top-revenue');
  return res.data.data ?? [];
};

// GET /products/categories → { status, message, data: [{category_name, ...}] }
export const getCategories = async (): Promise<CategoryStats[]> => {
  const res = await apiClient.get('/products/categories');
  return res.data.data ?? [];
};

// GET /products/category-trend → { status, message, data: [{year_month, category_name, order_count}] }
export const getCategoryTrend = async (): Promise<CategoryTrend[]> => {
  const res = await apiClient.get('/products/category-trend');
  return res.data.data ?? [];
};

// GET /products/dimensions → { status, message, data: [{category_name, avg_weight_g, avg_length_cm, avg_height_cm, avg_width_cm}] }
export const getProductDimensions = async (): Promise<ProductDimensions[]> => {
  const res = await apiClient.get('/products/dimensions');
  return res.data.data ?? [];
};
