import { api } from './api';

export interface Recommendation {
  id: string;
  type: 'budget_alert' | 'savings_tip' | 'spending_insight' | 'goal_tip' | 'anomaly';
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
  category: string;
  potential_savings: number;
  action: string;
  created_at: string;
}

export interface RecommendationsResponse {
  recommendations: Recommendation[];
  total_potential_savings: number;
}

export const recommendationsService = {
  getAll: async (): Promise<RecommendationsResponse> => {
    try {
      const response = await api.get<RecommendationsResponse>('/api/v1/recommendations');
      return response.data;
    } catch (error) {
      // Mock data as fallback
      return {
        recommendations: [],
        total_potential_savings: 0,
      };
    }
  },
  getRandom: async (): Promise<Recommendation> => {
    try {
      const response = await api.get<Recommendation>('/api/v1/recommendations/test-random');
      return response.data;
    } catch (error) {
      // Fallback mock recommendation
      return {
        id: `random_${Date.now()}`,
        type: 'savings_tip',
        title: 'Smart Saving Tip',
        description: 'Start small: Save just 50 TND per week and you\'ll have 2,600 TND by year end!',
        severity: 'info',
        category: 'Savings',
        potential_savings: 200,
        action: 'Set up weekly auto-transfer',
        created_at: new Date().toISOString(),
      };
    }
  },

  dismiss: async (id: string) => {
    await api.post(`/api/v1/recommendations/dismiss/${id}`);
  },
};
