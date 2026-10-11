export interface PaymentSummary {
  total_payment_value: number;
  avg_installments: number;
  most_popular_type: string;
  total_transactions: number;
  status: string;
}

export interface InstallmentDist {
  installments: number;
  count: number;
  total_value: number;
}

export interface MonthlyPayment {
  month: string;
  total_value: number;
  transaction_count: number;
}

export interface PaymentTypeSplit {
  payment_type: string;
  count: number;
  total_value: number;
}
