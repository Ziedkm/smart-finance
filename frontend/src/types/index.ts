export interface Transaction {
  id: string;
  amount: number;
  category: string;
  description: string;
  merchant?: string;
  transaction_date: string;
  transaction_type: 'income' | 'expense';
  payment_method?: string;
}

export interface Budget {
  id: string;
  category: string;
  amount: number;
  spent: number;
  period: 'weekly' | 'monthly' | 'yearly';
  variance: number;
}

export interface Goal {
  id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline: string;
  progress: number;
  status: 'active' | 'completed' | 'paused';
}

export interface Anomaly {
  id: string;
  transaction_id: string;
  amount: number;
  category: string;
  description: string;
  date: string;
  anomaly_score: number;
  severity: 'low' | 'medium' | 'high';
  explanation: string;
}

export interface KPIs {
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  budget_adherence: number;
}
