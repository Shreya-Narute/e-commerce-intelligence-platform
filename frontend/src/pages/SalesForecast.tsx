import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
} from 'recharts';
import { LineChart as LineChartIcon, AlertTriangle } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getRevenueForecast } from '../services/forecastingService';
import { ForecastResult } from '../types/forecasting';

const fmtCurrency = (v: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

export const SalesForecast: React.FC = () => {
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const f = await getRevenueForecast();
      setForecast(f);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load forecast data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) return <LoadingState message="Loading Sales Forecast..." subtext="Running time series forecasting model" />;
  if (error) return <ErrorState title="Forecast Unavailable" message={error} onRetry={fetchAll} />;
  if (forecast?.status === 'insufficient_data' || forecast?.status === 'no_data') {
    return (
      <EmptyState
        title="Insufficient Data for Forecasting"
        description="Sales forecasting requires at least 6 months of order data. Please ingest the Olist dataset first."
        stageBadge="Sales Forecasting"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<LineChartIcon className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  // Merge historical + forecast into a single chart-ready array
  const historicalPoints = (forecast?.historical ?? []).map((p) => ({
    period: p.period,
    historical: p.value,
    forecast: null as number | null,
    lower: null as number | null,
    upper: null as number | null,
  }));
  const forecastPoints = (forecast?.forecast ?? []).map((p) => ({
    period: p.period,
    historical: null as number | null,
    forecast: p.forecast,
    lower: p.lower_bound ?? null,
    upper: p.upper_bound ?? null,
  }));
  const chartData = [...historicalPoints, ...forecastPoints];
  const firstForecastPeriod = forecastPoints[0]?.period;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          Sales Forecasting
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Revenue Forecast</h2>
        <p className="text-xs text-slate-400 mt-0.5">Historical revenue with 3-month forward projection using {forecast?.metric ?? 'time series model'}.</p>
      </div>

      {/* Model Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
      </div>

      {/* Forecast Chart */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-white">Revenue: Historical + 3-Month Forecast</h3>
          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5"><span className="inline-block w-5 h-0.5 bg-indigo-400" /> Historical</span>
            <span className="flex items-center gap-1.5"><span className="inline-block w-5 border-t-2 border-dashed border-amber-400" /> Forecast</span>
          </div>
        </div>
        {chartData.length === 0 ? (
          <p className="text-xs text-slate-400">No forecast data available.</p>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 4, right: 24, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="period" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(v, name) => {
                    const num = typeof v === 'number' ? v : null;
                    const label = name === 'Historical Revenue' ? 'Historical' : 'Forecast';
                    return [num !== null ? fmtCurrency(num) : '—', label];
                  }}
                />
                {firstForecastPeriod && (
                  <ReferenceLine x={firstForecastPeriod} stroke="#334155" strokeDasharray="4 4" label={{ value: 'Forecast start', fill: '#64748b', fontSize: 10, position: 'top' }} />
                )}
                <Line
                  type="monotone"
                  dataKey="historical"
                  stroke="#6366f1"
                  strokeWidth={2}
                  dot={false}
                  connectNulls={false}
                  name="Historical Revenue"
                />
                <Line
                  type="monotone"
                  dataKey="forecast"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  strokeDasharray="6 3"
                  dot={{ r: 4, fill: '#f59e0b' }}
                  connectNulls={false}
                  name="Forecast Revenue"
                />
                <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* MAPE if available */}
      {forecast?.mape !== null && forecast?.mape !== undefined && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300">
          <AlertTriangle className="h-4 w-4 text-amber-400 flex-shrink-0" />
          <span>MAPE (Mean Absolute Percentage Error): <strong className="text-white">{fmtCurrency(forecast.mape)}</strong> (absolute value, lower is better).</span>
        </div>
      )}
    </div>
  );
};
