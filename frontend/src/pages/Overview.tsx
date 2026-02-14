import { useEffect, useState } from 'react';
import { KPICard } from '../components/dashboard/KPICard';
import { CategoryChart } from '../components/dashboard/CategoryChart';
import { TrendChart } from '../components/dashboard/TrendChart';
import { BudgetProgress } from '../components/dashboard/BudgetProgress';
import { dashboardService } from '../services/dashboard';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { exportDashboard } from '../utils/export';
import { 
  BanknotesIcon, 
  ArrowTrendingDownIcon, 
  ChartBarIcon,
  FlagIcon 
} from '@heroicons/react/24/outline';

export function Overview() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const dashboardData = await dashboardService.getData();
      setData(dashboardData);
      setError(null);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
          <p className="mt-2 text-sm text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={loadDashboard} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">
              <img src="..../logo.png" alt="" /> Smart Finance
            </h1>
          </div>
          <p className="mt-1 text-sm sm:text-base text-gray-500">
            Your financial overview for {new Date().toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })}
          </p>
        </div>
        <button
          onClick={() => exportDashboard(data)}
          className="hidden sm:flex btn-secondary items-center"
        >
          <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
          Export
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Income"
          value={`${data.total_income.toFixed(0)} TND`}
          trend={{ value: 5.2, isPositive: true }}
          icon={<BanknotesIcon className="h-6 w-6" />}
        />
        <KPICard
          title="Total Expenses"
          value={`${data.total_expenses.toFixed(0)} TND`}
          trend={{ value: 3.1, isPositive: false }}
          icon={<ArrowTrendingDownIcon className="h-6 w-6" />}
        />
        <KPICard
          title="Net Savings"
          value={`${data.net_savings.toFixed(0)} TND`}
          subtitle={`${data.savings_rate.toFixed(1)}% savings rate`}
          icon={<ChartBarIcon className="h-6 w-6" />}
        />
        <KPICard
          title="Budget Adherence"
          value={`${data.budget_adherence.toFixed(1)}%`}
          subtitle={data.budget_adherence >= 90 ? 'Excellent!' : 'Needs attention'}
          icon={<FlagIcon className="h-6 w-6" />}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <CategoryChart data={data.categories} />
        <BudgetProgress budgets={data.budgets} />
      </div>

      {/* Charts Row 2 */}
      <TrendChart data={data.trends} />
    </div>
  );
}
