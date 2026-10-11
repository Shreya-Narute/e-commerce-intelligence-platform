import { apiClient } from './api';
import { PaymentSummary, InstallmentDist, MonthlyPayment, PaymentTypeSplit } from '../types/payments';

// GET /payments/summary → { status, message, data: { total_payment_value, avg_installments, payment_type_breakdown:[...] } }
export const getPaymentSummary = async (): Promise<PaymentSummary> => {
  const res = await apiClient.get('/payments/summary');
  const d = res.data.data ?? {};
  const breakdown: { payment_type: string; total_value: number; transaction_count: number }[] =
    d.payment_type_breakdown ?? [];
  const top = breakdown.sort((a, b) => b.total_value - a.total_value)[0];
  return {
    status: res.data.status,
    total_payment_value: d.total_payment_value ?? 0,
    avg_installments: d.avg_installments ?? 0,
    most_popular_type: top?.payment_type ?? '—',
    total_transactions: breakdown.reduce((acc, b) => acc + (b.transaction_count ?? 0), 0),
  };
};

// GET /payments/installment-distribution → { status, message, data: [{installments, count}] }
export const getInstallmentDistribution = async (): Promise<InstallmentDist[]> => {
  const res = await apiClient.get('/payments/installment-distribution');
  return (res.data.data ?? []).map((item: { installments: string | number; count: number }) => ({
    installments: typeof item.installments === 'string' ? parseInt(item.installments) : item.installments,
    count: item.count,
    total_value: 0,  // not provided
  }));
};

// GET /payments/monthly-volume → { status, message, data: [{year_month, total_value, transaction_count}] }
export const getMonthlyVolume = async (): Promise<MonthlyPayment[]> => {
  const res = await apiClient.get('/payments/monthly-volume');
  return (res.data.data ?? []).map((item: { year_month: string; total_value: number; transaction_count: number }) => ({
    month: item.year_month,  // field name mapping
    total_value: item.total_value,
    transaction_count: item.transaction_count,
  }));
};

// GET /sales/payment-types → { status, message, data: [{payment_type, revenue, transaction_count}] }
export const getPaymentTypeSplit = async (): Promise<PaymentTypeSplit[]> => {
  const res = await apiClient.get('/sales/payment-types');
  return (res.data.data ?? []).map((item: { payment_type: string; revenue: number; transaction_count: number }) => ({
    payment_type: item.payment_type,
    count: item.transaction_count,
    total_value: item.revenue,
  }));
};
