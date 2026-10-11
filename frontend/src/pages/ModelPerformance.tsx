import React, { useEffect, useState } from 'react';
import { Cpu, BarChart2 } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getRFMSegments } from '../services/rfmService';
import { getRevenueForecast } from '../services/forecastingService';
import { RFMSummary } from '../types/rfm';
import { ForecastResult } from '../types/forecasting';

const fmtCurrency = (v: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

export const ModelPerformance: React.FC = () => {
  const [rfm, setRfm] = useState<RFMSummary | null>(null);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [r, f] = await Promise.all([getRFMSegments(), getRevenueForecast()]);
      setRfm(r);
      setForecast(f);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load model metrics';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) return <LoadingState message="Loading Model Performance Metrics..." subtext="Fetching RFM clustering and forecasting evaluation scores" />;
  if (error) return <ErrorState title="Model Metrics Unavailable" message={error} onRetry={fetchAll} />;

  const noRFMData = rfm?.status === 'no_data' || rfm?.status === 'insufficient_data';
  const noForecastData = forecast?.status === 'no_data' || forecast?.status === 'insufficient_data';

  if (noRFMData && noForecastData) {
    return (
      <EmptyState
        title="Models Not Yet Run"
        description="Analytics models have not been executed yet. Ingest the Olist dataset and run the analytics pipeline to populate model metrics."
        stageBadge="Model Performance"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<Cpu className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          Model Performance
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">ML Model Evaluation</h2>
        <p className="text-xs text-slate-400 mt-0.5">Diagnostic metrics for RFM clustering and revenue forecasting models.</p>
      </div>

      {/* RFM Section */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center gap-2">
          <BarChart2 className="h-4 w-4 text-indigo-400" />
          <h3 className="text-sm font-semibold text-white">RFM Clustering Model</h3>
        </div>

        {noRFMData ? (
          <p className="p-5 text-xs text-slate-400">RFM model has not been run yet — no data available.</p>
        ) : (
          <div className="p-5 space-y-4">
            {/* Silhouette Score */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-400">Silhouette Score (cluster quality)</span>
                <span className="text-sm font-bold text-indigo-300">
                  {rfm?.silhouette_score !== null && rfm?.silhouette_score !== undefined
                    ? rfm.silhouette_score.toFixed(3)
                    : '—'}
                </span>
              </div>
              {rfm?.silhouette_score !== null && rfm?.silhouette_score !== undefined && (
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 rounded-full"
                    style={{ width: `${Math.max(0, Math.min(1, rfm.silhouette_score)) * 100}%` }}
                  />
                </div>
              )}
              <p className="text-[11px] text-slate-500 mt-1">Range: -1 (poor) to 1 (perfect). Scores above 0.3 indicate meaningful separation.</p>
            </div>

            {/* Cluster sizes */}
            {rfm?.segments && rfm.segments.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-slate-300 mb-3">Cluster Sizes</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left text-slate-300">
                    <thead className="bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="py-2.5 px-4">Segment</th>
                        <th className="py-2.5 px-4">Customers</th>
                        <th className="py-2.5 px-4">% of Total</th>
                        <th className="py-2.5 px-4">Avg Recency</th>
                        <th className="py-2.5 px-4">Avg Frequency</th>
                        <th className="py-2.5 px-4">Avg Monetary</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {rfm.segments.map((seg, i) => {
                        const pct = rfm.total_customers > 0 ? ((seg.customer_count / rfm.total_customers) * 100).toFixed(1) : '—';
                        return (
                          <tr key={i} className="hover:bg-slate-800/30">
                            <td className="py-2.5 px-4 font-medium text-slate-200">{seg.segment}</td>
                            <td className="py-2.5 px-4 font-mono">{seg.customer_count.toLocaleString()}</td>
                            <td className="py-2.5 px-4 font-mono">{pct}%</td>
                            <td className="py-2.5 px-4 font-mono">{seg.avg_recency_days.toFixed(0)}</td>
                            <td className="py-2.5 px-4 font-mono">{seg.avg_frequency.toFixed(1)}</td>
                            <td className="py-2.5 px-4 font-mono">{fmtCurrency(seg.avg_monetary)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Forecasting Section */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center gap-2">
          <Cpu className="h-4 w-4 text-indigo-400" />
          <h3 className="text-sm font-semibold text-white">Revenue Forecasting Model</h3>
          {forecast?.metric && <span className="text-[11px] text-slate-400 ml-2">({forecast.metric})</span>}
        </div>

        {noForecastData ? (
          <p className="p-5 text-xs text-slate-400">Forecasting model has not been run yet — insufficient data.</p>
        ) : (
          <div className="p-5">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <StatCard
                label="MAE"
                value={forecast?.mae !== null && forecast?.mae !== undefined ? fmtCurrency(forecast.mae) : '—'}
                subtext="Mean Absolute Error"
                variant="info"
              />
              <StatCard
                label="RMSE"
                value={forecast?.rmse !== null && forecast?.rmse !== undefined ? fmtCurrency(forecast.rmse) : '—'}
                subtext="Root Mean Squared Error"
                variant="info"
              />
              <StatCard
                label="MAPE"
                value={
                  forecast?.mape !== null && forecast?.mape !== undefined
                    ? fmtCurrency(forecast.mape)
                    : '—'
                }
                subtext="Mean Absolute Percentage Error (absolute)"
                variant="info"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
