import { api } from './api';

export interface Transaction {
  id: string;
  user_id: string;
  amount: number;
  category: string;
  description: string;
  merchant?: string;
  transaction_date: string;
  transaction_type: 'income' | 'expense';
  payment_method?: string;
  tags?: string[];
  created_at: string;
}

export interface CreateTransactionDTO {
  amount: number;
  category?: string;
  description: string;
  merchant?: string;
  transaction_date: string;
  transaction_type: 'income' | 'expense';
  payment_method?: string;
  tags?: string[];
}

export const transactionService = {
  // Get all transactions
  getAll: async () => {
    const response = await api.get<Transaction[]>('/api/v1/transactions');
    return response.data;
  },

  // Create transaction (with AI classification)
  create: async (data: CreateTransactionDTO) => {
    const response = await api.post<Transaction>('/api/v1/transactions', data);
    return response.data;
  },

  // Update transaction
  update: async (id: string, data: Partial<CreateTransactionDTO>) => {
    const response = await api.patch<Transaction>(`/api/v1/transactions/${id}`, data);
    return response.data;
  },

  // Delete transaction
  delete: async (id: string) => {
    await api.delete(`/api/v1/transactions/${id}`);
  },
};
