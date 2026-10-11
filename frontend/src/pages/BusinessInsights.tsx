import React, { useEffect, useState } from 'react';
import {
  Lightbulb,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';

import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getInsightsSummary } from '../services/insightsService';
import { InsightsSummary, InsightItem } from '../types/insights';

const sentimentConfig = {
  positive: {
    border: 'border-emerald-800/40',
    bg: 'bg-emerald-950/20',
    badge:
      'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
    value: 'text-emerald-400',
    icon: TrendingUp,
    iconColor: 'text-emerald-400',
  },
  neutral: {
    border: 'border-amber-800/40',
    bg: 'bg-amber-950/20',
    badge:
      'bg-amber-500/10 text-amber-400 border border-amber-500/20',
    value: 'text-amber-400',
    icon: Minus,
    iconColor: 'text-amber-400',
  },
  negative: {
    border: 'border-red-800/40',
    bg: 'bg-red-950/20',
    badge:
      'bg-red-500/10 text-red-400 border border-red-500/20',
    value: 'text-red-400',
    icon: TrendingDown,
    iconColor: 'text-red-400',
  },
};

type Sentiment = keyof typeof sentimentConfig;

const getSentiment = (sentiment: unknown): Sentiment => {
  if (typeof sentiment !== 'string') {
    return 'neutral';
  }

  const normalized = sentiment.toLowerCase().trim();

  if (
    normalized === 'positive' ||
    normalized === 'neutral' ||
    normalized === 'negative'
  ) {
    return normalized;
  }

  return 'neutral';
};

const getDisplayText = (value: unknown, fallback = '—'): string => {
  return typeof value === 'string' && value.trim().length > 0
    ? value
    : fallback;
};

const InsightCard: React.FC<{ insight: InsightItem }> = ({
  insight,
}) => {
  const sentiment = getSentiment(insight?.sentiment);
  const cfg = sentimentConfig[sentiment];
  const Icon = cfg.icon;

  const sentimentLabel =
    sentiment.charAt(0).toUpperCase() + sentiment.slice(1);

  return (
    <div
      className={`rounded-2xl border ${cfg.border} ${cfg.bg} p-5 flex flex-col gap-3`}
    >
      <div className="flex items-start justify-between gap-2">
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium ${cfg.badge}`}
        >
          <Icon className={`h-3.5 w-3.5 ${cfg.iconColor}`} />
          {sentimentLabel}
        </span>
      </div>

      <div>
        <h4 className="text-sm font-semibold text-white">
          {getDisplayText(insight?.title, 'Untitled Insight')}
        </h4>

        <div className={`text-2xl font-bold mt-1 ${cfg.value}`}>
          {getDisplayText(insight?.value)}
        </div>
      </div>

      <p className="text-[11px] text-slate-400 leading-relaxed">
        {getDisplayText(insight?.context, 'No additional context available.')}
      </p>

      <div className="pt-3 border-t border-slate-800/60">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
          Recommendation
        </span>

        <p className="text-xs text-slate-300 mt-1 leading-relaxed">
          {getDisplayText(
            insight?.recommendation,
            'No recommendation available.'
          )}
        </p>
      </div>
    </div>
  );
};

export const BusinessInsights: React.FC = () => {
  const [insights, setInsights] = useState<InsightsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getInsightsSummary();
      setInsights(data ?? null);
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : 'Failed to load business insights';

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchAll();
  }, []);

  if (loading) {
    return (
      <LoadingState
        message="Generating Business Insights..."
        subtext="Analysing platform metrics for actionable recommendations"
      />
    );
  }

  if (error) {
    return (
      <ErrorState
        title="Insights Unavailable"
        message={error}
        onRetry={fetchAll}
      />
    );
  }

  const insightList: InsightItem[] = Array.isArray(insights?.insights)
    ? insights.insights.filter(
        (item): item is InsightItem =>
          item !== null &&
          typeof item === 'object'
      )
    : [];

  if (insights?.status === 'no_data' || insightList.length === 0) {
    return (
      <EmptyState
        title="No Business Insights Available"
        description="Business insights are generated from live data. Ingest the Olist dataset and run analytics modules first."
        stageBadge="Business Insights"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<Lightbulb className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  const positive = insightList.filter(
    (item) => getSentiment(item.sentiment) === 'positive'
  ).length;

  const neutral = insightList.filter(
    (item) => getSentiment(item.sentiment) === 'neutral'
  ).length;

  const negative = insightList.filter(
    (item) => getSentiment(item.sentiment) === 'negative'
  ).length;

  const generatedDate =
    typeof insights?.generated_at === 'string'
      ? insights.generated_at.slice(0, 10)
      : '—';

  return (
    <div className="space-y-6">
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          Business Insights
        </div>

        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Business Insights &amp; Recommendations
            </h2>

            <p className="text-xs text-slate-400 mt-0.5">
              Automated insights derived from verified platform data.
              Generated at {generatedDate}.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <TrendingUp className="h-3.5 w-3.5" />
              {positive} positive
            </span>

            <span className="flex items-center gap-1.5 text-amber-400">
              <Minus className="h-3.5 w-3.5" />
              {neutral} neutral
            </span>

            <span className="flex items-center gap-1.5 text-red-400">
              <TrendingDown className="h-3.5 w-3.5" />
              {negative} concerning
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {insightList.map((insight, index) => (
          <InsightCard
            key={`${getDisplayText(insight.title, 'insight')}-${index}`}
            insight={insight}
          />
        ))}
      </div>
    </div>
  );
};