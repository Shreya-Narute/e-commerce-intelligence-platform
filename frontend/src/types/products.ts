// Matches /products/top-revenue response items
export interface ProductRevenue {
  product_id: string;
  category_name: string;  // API field name
  revenue: number;
  order_count: number;
}

// Matches /products/categories response items
export interface CategoryStats {
  category_name: string;  // API field name
  revenue: number;
  order_count: number;
  avg_price?: number;
}

// Matches /products/category-trend response items
export interface CategoryTrend {
  year_month: string;      // API field name
  category_name: string;   // API field name
  order_count: number;
}

// Matches /products/dimensions response items
export interface ProductDimensions {
  category_name: string;   // API field name — grouped by category, not product
  avg_weight_g: number;
  avg_length_cm: number;
  avg_height_cm: number;
  avg_width_cm: number;
}
