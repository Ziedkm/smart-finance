import { api } from './api';

export interface Goal {
  id: string;
  user_id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
  status: 'active' | 'completed' | 'paused';
  created_at: string;
}

export interface CreateGoalDTO {
  name: string;
  target_amount: number;
  current_amount?: number;
  deadline: string;
  category: string;
  priority?: 'low' | 'medium' | 'high';
}

export const goalService = {
  getAll: async () => {
    const response = await api.get<Goal[]>('/api/v1/goals');
    return response.data;
  },

  create: async (data: CreateGoalDTO) => {
    const response = await api.post<Goal>('/api/v1/goals', data);
    return response.data;
  },

  update: async (id: string, data: Partial<CreateGoalDTO>) => {
    const response = await api.patch<Goal>(`/api/v1/goals/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/api/v1/goals/${id}`);
  },
};
