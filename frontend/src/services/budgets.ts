import { api } from './api';

export interface Budget {
  id: string;
  user_id: string;
  category: string;
  amount: number;
  period: 'weekly' | 'monthly' | 'yearly';
  start_date: string;
  end_date?: string;
  alert_threshold: number;
  created_at: string;
}

export interface CreateBudgetDTO {
  category: string;
  amount: number;
  period: 'weekly' | 'monthly' | 'yearly';
  start_date: string;
  end_date?: string;
  alert_threshold?: number;
}

export const budgetService = {
  getAll: async () => {
    const response = await api.get<Budget[]>('/api/v1/budgets');
    return response.data;
  },

  create: async (data: CreateBudgetDTO) => {
    const response = await api.post<Budget>('/api/v1/budgets', data);
    return response.data;
  },

  update: async (id: string, data: Partial<CreateBudgetDTO>) => {
    const response = await api.patch<Budget>(`/api/v1/budgets/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/api/v1/budgets/${id}`);
  },
};
