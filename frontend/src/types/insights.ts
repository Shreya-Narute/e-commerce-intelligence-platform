export interface InsightItem {
  title: string;
  value: string;
  context: string;
  recommendation: string;
  sentiment: 'positive' | 'neutral' | 'negative';
}

export interface InsightsSummary {
  insights: InsightItem[];
  generated_at: string;
  status: string;
}
