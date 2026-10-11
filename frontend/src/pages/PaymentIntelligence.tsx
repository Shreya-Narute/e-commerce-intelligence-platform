import React, { useEffect, useState } from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { CreditCard, DollarSign, Hash } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getPaymentSummary, getInstallmentDistribution, getMonthlyVolume, getPaymentTypeSplit } from '../services/paymentsService';
import { PaymentSummary, InstallmentDist, MonthlyPayment, PaymentTypeSplit } from '../types/payments';

const CHART_COLORS = ['#6366f1', '#22d3ee', '#f59e0b', '#10b981', '#f43f5e'];

const fmtCurrency = (v: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

export const PaymentIntelligence: React.FC = () => {
  const [summary, setSummary] = useState<PaymentSummary | null>(null);
  const [installments, setInstallments] = useState<InstallmentDist[]>([]);
  const [monthly, setMonthly] = useState<MonthlyPayment[]>([]);
  const [typeSplit, setTypeSplit] = useState<PaymentTypeSplit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, i, m, t] = await Promise.all([
        getPaymentSummary(),
        getInstallmentDistribution(),
        getMonthlyVolume(),
        getPaymentTypeSplit(),
      ]);
      setSummary(s);
      setInstallments(i);
      setMonthly(m);
      setTypeSplit(t);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load payment data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) return <LoadingState message="Loading Payment Intelligence..." subtext="Analysing payment types, installments, and transaction volumes" />;
  if (error) return <ErrorState title="Payment Data Unavailable" message={error} onRetry={fetchAll} />;
  if (summary?.status === 'no_data') {
    return (
      <EmptyState
        title="No Payment Data Available"
        description="The order_payments table is empty. Run the ingestion pipeline first."
        stageBadge="Payment Intelligence"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<CreditCard className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          Payment Intelligence
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Payment Behaviour Analysis</h2>
        <p className="text-xs text-slate-400 mt-0.5">Payment methods, installment patterns, and transaction volume over time.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Total Payment Value"
          value={fmtCurrency(summary?.total_payment_value ?? 0)}
          subtext="Cumulative transactions"
          icon={<DollarSign className="h-4 w-4" />}
          variant="success"
        />
        <StatCard
          label="Avg Installments"
          value={(summary?.avg_installments ?? 0).toFixed(1)}
          subtext="Average installments per order"
          icon={<Hash className="h-4 w-4" />}
          variant="info"
        />
        <StatCard
          label="Most Popular Type"
          value={summary?.most_popular_type ?? '—'}
          subtext="Dominant payment method"
          icon={<CreditCard className="h-4 w-4" />}
          variant="default"
        />
      </div>

      {/* Payment Type Pie + Installment Bar row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Payment Type Pie */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Payment Type Distribution</h3>
          {typeSplit.length === 0 ? (
            <p className="text-xs text-slate-400">No payment type data available.</p>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={typeSplit}
                    dataKey="count"
                    nameKey="payment_type"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label={({ payment_type, percent }) => `${payment_type} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {typeSplit.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number) => [v.toLocaleString(), 'Transactions']}
                  />
                  <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Installment Distribution */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Installment Distribution</h3>
          {installments.length === 0 ? (
            <p className="text-xs text-slate-400">No installment data available.</p>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={installments} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="installments" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} label={{ value: 'Installments', position: 'insideBottom', fill: '#64748b', fontSize: 11, dy: 8 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => v.toLocaleString()} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number) => [v.toLocaleString(), 'Orders']}
                  />
                  <Bar dataKey="count" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Monthly Payment Volume */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Monthly Payment Volume</h3>
        {monthly.length === 0 ? (
          <p className="text-xs text-slate-400">No monthly payment data available.</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthly} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="paymentGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [fmtCurrency(v), 'Payment Value']}
                />
                <Area type="monotone" dataKey="total_value" stroke="#6366f1" strokeWidth={2} fill="url(#paymentGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};
