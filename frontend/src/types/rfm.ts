// Matches backend analytics/rfm.py segment output
export interface RFMSegment {
  segment: string;
  customer_count: number;
  avg_recency_days: number;   // field name in API is avg_recency_days
  avg_frequency: number;
  avg_monetary: number;
}

// Matches backend rfm score_distribution output
export interface RFMDistributionItem {
  score: number;
  r_count: number;
  f_count: number;
  m_count: number;
}

/** @deprecated kept for legacy compat, use RFMDistributionItem */
export type RFMDistribution = RFMDistributionItem;

// Matches backend rfm customers list output
export interface RFMCustomer {
  customer_unique_id: string;  // API field name
  recency_days: number;        // API field name
  frequency: number;
  monetary: number;
  segment: string;
  r_score: number;
  f_score: number;
  m_score: number;
  cluster: number;
}

// Top-level response from getRFMSegments()
export interface RFMSummary {
  status: string;
  message?: string;
  reference_date?: string;
  total_customers: number;
  silhouette_score: number | null;
  segments: RFMSegment[];
}
