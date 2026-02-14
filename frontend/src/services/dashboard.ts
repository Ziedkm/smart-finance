import { api } from './api';

export interface DashboardData {
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  budget_adherence: number;
  categories: Array<{
    category: string;
    amount: number;
    percentage: number;
  }>;
  trends: Array<{
    date: string;
    income: number;
    expenses: number;
  }>;
  budgets: Array<{
    category: string;
    spent: number;
    budget: number;
    variance: number;
  }>;
}

export const dashboardService = {
  // Get full dashboard data
  getData: async (): Promise<DashboardData> => {
    try {
      const response = await api.get<any>('/api/v1/dashboard');
      return response.data;
    } catch (error) {
      console.error('Dashboard API error:', error);
      // Return mock data as fallback
      return getMockDashboardData();
    }
  },

  // Test endpoint (no auth required)
  getTestData: async () => {
    try {
      const response = await api.get('/test/info');
      return response.data;
    } catch (error) {
      console.error('Test API error:', error);
      throw error;
    }
  },
};

// Mock data for development
function getMockDashboardData(): DashboardData {
  return {
    total_income: 4500,
    total_expenses: 2850,
    net_savings: 1650,
    savings_rate: 36.7,
    budget_adherence: 89.5,
    categories: [
      { category: 'Groceries', amount: 850, percentage: 29.8 },
      { category: 'Transport', amount: 450, percentage: 15.8 },
      { category: 'Dining', amount: 380, percentage: 13.3 },
      { category: 'Bills & Utilities', amount: 620, percentage: 21.8 },
      { category: 'Entertainment', amount: 300, percentage: 10.5 },
      { category: 'Other', amount: 250, percentage: 8.8 },
    ],
    trends: [
      { date: 'Week 1', income: 1125, expenses: 680 },
      { date: 'Week 2', income: 1125, expenses: 720 },
      { date: 'Week 3', income: 1125, expenses: 650 },
      { date: 'Week 4', income: 1125, expenses: 800 },
    ],
    budgets: [
      { category: 'Groceries', spent: 850, budget: 800, variance: 50 },
      { category: 'Transport', spent: 450, budget: 500, variance: -50 },
      { category: 'Dining', spent: 380, budget: 400, variance: -20 },
      { category: 'Bills & Utilities', spent: 620, budget: 600, variance: 20 },
    ],
  };
}
